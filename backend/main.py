import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from langfuse import observe,get_client


from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# Importación de parsers propios
from src.image_parser import extract_from_pdf, extract_from_image

#Modelo de datos y agentes
from src.models import ContractChangeOutput
from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent

load_dotenv()

# Verificar que las API keys estén configuradas
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

app = FastAPI(title="LegalMove - Contract Comparison API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

langfuse = get_client()

# Esquema para forzar una respuesta booleana estructurada
class DocumentValidation(BaseModel):
    is_legal_document: bool = Field(description="True si el texto pertenece a un contrato, adenda o documento legal, False si es basura o imágenes irrelevantes.")
    detected_language: str = Field(description="Idioma detectado (ES, EN, FR, etc.)")

def validate_legal_nature(text_sample: str):
    # Solo enviamos los primeros 500 caracteres para ahorrar tokens
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) # gpt-4o-mini es perfecto y barato para esto
    structured_llm = llm.with_structured_output(DocumentValidation)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un experto en clasificación de documentos multilingüe. Tu única tarea es determinar si el texto proporcionado tiene naturaleza legal (contratos, acuerdos, adendas) sin importar el idioma."),
        ("user", "Analiza este extracto y determina si es un documento legal: {sample}")
    ])
    
    chain = prompt | structured_llm
    return chain.invoke({"sample": text_sample[:500]})


@app.post("/extract")
@observe(name="init_pipeline", as_type="generation")
async def extract_words(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    #Implementing Langfuse Tracing
    span = langfuse.start_observation(name="start_pipeline")
    results_parsing = {}


    step1_read_files_span = span.start_observation(name="step1_read_files", as_type="generation")
    # Parsing Multimodal / gpt-4o
    for upload_file in [file1, file2]:
        content = await upload_file.read()
        filename = upload_file.filename or "unknown"
        
        try: 
            # Extracción de palabras (devuelve lista de strings)
            if filename.lower().endswith(".pdf"):
                words = extract_from_pdf(content)
            else:
                words = extract_from_image(content)
        except Exception as e:
            return JSONResponse(
                status_code=422,
                content={
                    "legal_analysis": {
                        "summary_of_the_change": f"ARCHIVO RECHAZADO: El documento '{filename}' no fue reconocido como un texto legal válido (Idioma detectado: {validation.detected_language}).",
                        "sections_changed": [],
                        "topics_touched": ["Fallo de Validación"]
                    }
                }
            )    

        results_parsing[filename] = {
            "word_count": len(words),
            "words": words
        }
    step1_read_files_span.end()


    garbage_collector_span = span.start_observation(name="garbage_collector", as_type="generation")
    # --- PASO INTERMEDIO: Validación Multilingüe ---
    for filename, info in results_parsing.items():
        sample_text = " ".join(info['words'][:100]) # Tomamos una muestra
        
        validation = validate_legal_nature(sample_text)
        
        if not validation.is_legal_document:
            return JSONResponse(
                status_code=422,
                content={
                    "legal_analysis": {
                        "summary_of_the_change": f"ARCHIVO RECHAZADO: El documento '{filename}' no fue reconocido como un texto legal válido (Idioma detectado: {validation.detected_language}).",
                        "sections_changed": [],
                        "topics_touched": ["Fallo de Validación"]
                    }
                }
            )    
    garbage_collector_span.end()


    step2_prepapring_texts_span = span.start_observation(name="step2_prepapring_texts", as_type="generation")
    # Preparación para Agentes
    listas = [info['words'] for info in results_parsing.values()]
    if len(listas) < 2:
        raise HTTPException(status_code=400, detail="Se necesitan dos archivos.")
    
    texto_contrato = " ".join(listas[0])
    texto_adenda = " ".join(listas[1])
    step2_prepapring_texts_span.end()

    # Flujo de Agentes 
    
    step3_contextualization_agent_span = span.start_observation(name="step3_contextualization_agent", as_type="generation")
    # Agente 1: Contexto
    agente1 = ContextualizationAgent()
    context_response = agente1.get_chain().invoke({
        "contrato_text": texto_contrato, 
        "adenda_text": texto_adenda
    })
    step3_contextualization_agent_span.end()

    step4_extraction_agent_span = span.start_observation(name="step4_extraction_agent", as_type="generation")
    # Agente 2: Extracción (JSON Estructurado)
    agente2 = ExtractionAgent()
    print(context_response.content)
    analisis_legal = agente2.get_chain().invoke({
        "context_map": context_response.content,
        "original_text": texto_contrato,
        "adenda_text": texto_adenda
    })
    step4_extraction_agent_span.end()

    
    
    # 4. Resultado Consolidado
    return JSONResponse(content={
        "document_data": results_parsing,
        "legal_analysis": analisis_legal.model_dump()
    })

    span.end()

@app.get("/health")
def health():
    return {"status": "ok"}
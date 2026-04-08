import os
import base64
from openai import OpenAI
from langfuse import Langfuse
from dotenv import load_dotenv

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import re
import io
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from typing import List
from src.image_parser import  extract_from_pdf, extract_from_image

#from src.agents.contextualization_agent import ContextualizationAgent
#from src.agents.extraction_agent import ExtractionAgent
#from src.agents.orchestrator import Orchestrator

from langfuse import observe



# Load environment variables
load_dotenv()

# Verificar que las API keys estén configuradas
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY no configurada. Crea un archivo .env basado en .env.example")

print("✅ Variables de entorno cargadas")
print(f"   OpenAI API Key: {'✓ configurada' if OPENAI_API_KEY else '✗ faltante'}")
print(f"   Langfuse Public Key: {'✓ configurada' if LANGFUSE_PUBLIC_KEY else '⚠ no configurada (opcional)'}")
print(f"   Langfuse Secret Key: {'✓ configurada' if LANGFUSE_SECRET_KEY else '⚠ no configurada (opcional)'}")



# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Initialize Langfuse  client
langfuse_client = Langfuse(secret_key=os.getenv("LANGFUSE_SECRET_KEY"))


app = FastAPI(title="File Word Extractor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

'''
def build_dragndrop_system(
    openai_client: client,
    langfuse_client=langfuse_client,
    force_rebuild: bool = False,
) -> Orchestrator:
    """
    Inicializa todo el sistema multi-agente.
    
    Args:
        openai_client: Cliente de OpenAI autenticado.
        langfuse_client: Cliente de Langfuse para observabilidad (opcional).
        force_rebuild: Reconstruir vector stores desde cero.
    
    Returns:
        Orquestador listo para recibir consultas.
    """
    print("\n🚀 Inicializando Sistema Multi-Agente TechCorp...\n")

    # 1. Construir / cargar vector stores
    vector_stores = build_all_vector_stores(openai_client, force_rebuild=force_rebuild)

    # 2. Inicializar agentes
    hr_agent = HRAgent(openai_client, vector_stores["hr"])
    tech_agent = TechAgent(openai_client, vector_stores["tech"])
    finance_agent = FinanceAgent(openai_client, vector_stores["finance"])

    # 3. Inicializar orquestador
    orchestrator = Orchestrator(
        openai_client=openai_client,
        hr_agent=hr_agent,
        tech_agent=tech_agent,
        finance_agent=finance_agent,
        langfuse_client=langfuse_client,
    )

    #total_chunks = sum(len(vs["chunks"]) for vs in vector_stores.values())
    #print(f"\n✅ Sistema listo. Total chunks indexados: {total_chunks}")
    #print("   - HR:", len(vector_stores["hr"]["chunks"]), "chunks")
    #print("   - Tech:", len(vector_stores["tech"]["chunks"]), "chunks")
    #print("   - Finance:", len(vector_stores["finance"]["chunks"]), "chunks")

    return orchestrator
'''

@observe(name="procesar_diccionario_contratos", as_type="generation")
def procesar_diccionario_contratos(datos_dict):
    """
    Recibe un diccionario y devuelve las listas de palabras
    sin los nombres de los archivos.
    """
    # Extraemos solo la lista de 'words' de cada valor en el diccionario
    listas_de_palabras = [info['words'] for info in datos_dict.values()]
    
    return listas_de_palabras


@app.post("/extract")
@observe(name="init_extract", as_type="generation")
async def extract_words(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    results = {}

    for upload_file in [file1, file2]:
        content = await upload_file.read()
        filename = upload_file.filename or "unknown"
        content_type = upload_file.content_type or ""

        try:
            if "pdf" in content_type or filename.lower().endswith(".pdf"):
                words = extract_from_pdf(content)
            elif any(ext in content_type for ext in ["image", "png", "jpg", "jpeg", "tiff", "bmp", "webp"]) or \
                 filename.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp", ".PDF")):
                words = extract_from_image(content)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type for '{filename}'. Only PDF and images are supported."
                )

            results[filename] = {
                "word_count": len(words),
                "words": words
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process '{filename}': {str(e)}"
            )



    # aca llegan los resultados para los agentes
    #print(results)
    info_contratos=results  
    resultado = procesar_diccionario_contratos(info_contratos)
    #print(resultado)
    lista_contratos=resultado[0]
    lista_adenda=resultado[1]
    print(lista_contratos)
    print(lista_adenda)    
    
    


    # redefinir results para generar un json acorde a models.py
    
    return JSONResponse(content=results)


@app.get("/health")
def health():
    return {"status": "ok"}

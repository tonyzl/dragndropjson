import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Importación de parsers propios
from src.image_parser import extract_from_pdf, extract_from_image

# IMPORTACIÓN CORREGIDA: Solo lo que existe en src.models
from src.models import ContractChangeOutput
from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent

load_dotenv()

app = FastAPI(title="LegalMove - Contract Comparison API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract")
async def extract_words(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    results_parsing = {}

    # 1. Parsing Multimodal / OCR
    for upload_file in [file1, file2]:
        content = await upload_file.read()
        filename = upload_file.filename or "unknown"
        
        # Extracción de palabras (devuelve lista de strings)
        if filename.lower().endswith(".pdf"):
            words = extract_from_pdf(content)
        else:
            words = extract_from_image(content)

        results_parsing[filename] = {
            "word_count": len(words),
            "words": words
        }

    # 2. Preparación para Agentes
    listas = [info['words'] for info in results_parsing.values()]
    if len(listas) < 2:
        raise HTTPException(status_code=400, detail="Se necesitan dos archivos.")
    
    texto_contrato = " ".join(listas[0])
    texto_adenda = " ".join(listas[1])

    # 3. Flujo de Agentes (Sin Try-Except para ver errores directos)
    # Agente 1: Contexto
    agente1 = ContextualizationAgent()
    context_response = agente1.get_chain().invoke({
        "contrato_text": texto_contrato, 
        "adenda_text": texto_adenda
    })

    # Agente 2: Extracción (JSON Estructurado)
    agente2 = ExtractionAgent()
    analisis_legal = agente2.get_chain().invoke({
        "context_map": context_response.content,
        "original_text": texto_contrato,
        "adenda_text": texto_adenda
    })

    # 4. Resultado Consolidado
    return JSONResponse(content={
        "document_data": results_parsing,
        "legal_analysis": analisis_legal.model_dump()
    })

@app.get("/health")
def health():
    return {"status": "ok"}
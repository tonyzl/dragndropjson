import os
import base64
from openai import OpenAI
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
from src.agents.extraction_agent import  extract_from_pdf, extract_from_image


# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="File Word Extractor API")

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

    
    # redefinir results para generar un json acorde a models.py
    
    return JSONResponse(content=results)


@app.get("/health")
def health():
    return {"status": "ok"}

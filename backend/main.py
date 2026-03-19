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
from src.agents.extraction_agent import  extract_and_save_form_data


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


def extract_words_from_text(text: str) -> List[str]:
    words = re.findall(r'\b\w+\b', text)
    return [w for w in words if w.strip()]


def extract_from_pdf(file_bytes: bytes) -> List[str]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return extract_words_from_text(full_text)


def extract_from_image(file_bytes: bytes) -> List[str]:
    base64_image = base64.b64encode(file_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                    {
                        "type": "text",
                        "text": "Extract all words from this image. Return only the words, one per line, with no extra commentary."
                    }
                ],
            }
        ],
    )

    text = response.choices[0].message.content
    print(text)
    return extract_words_from_text(text)


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

    return JSONResponse(content=results)


@app.get("/health")
def health():
    return {"status": "ok"}

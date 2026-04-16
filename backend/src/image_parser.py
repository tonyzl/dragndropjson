import os
import re
import base64
import fitz  # PyMuPDF
from openai import OpenAI
from dotenv import load_dotenv
import io
from PIL import Image
from typing import List

# Pydantic Schema for structured output
#from src.models import FormFields

from langfuse import observe, get_client
from langfuse.langchain import CallbackHandler




# Load environment variables
load_dotenv()

# Verificar que las API keys estén configuradas
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")



# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

langfuse = get_client()
langfuse_handler = CallbackHandler()


def extract_words_from_text(text: str) -> List[str]:
    words = re.findall(r'\b\w+\b', text)
    return [w for w in words if w.strip()]




@observe(name="extract_from_pdf", as_type="generation")
def extract_from_pdf(file_bytes: bytes) -> list[str]:
    #client = OpenAI()

    #span = langfuse.start_observation(as_type="generation", name="span_extract_from_pdf", model="gpt-4o") 
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    
    all_words = []
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0

    for page in doc:
        # Render page to image (2x zoom for better resolution)
        mat = fitz.Matrix(0.5, 0.5)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("jpeg")
        base64_image = base64.b64encode(img_bytes).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                        {
                            "type": "text",
                            "text": "Extract all words from this image. Return only the words, one per line, with no extra commentary."
                        }
                    ],
                }
            ],
            
        )

        raw_text = response.choices[0].message.content
        total_tokens += response.usage.total_tokens
        prompt_tokens += response.usage.prompt_tokens
        completion_tokens += response.usage.completion_tokens


        config={"callbacks": [langfuse_handler]}
        all_words.extend(extract_words_from_text(raw_text))
        

    doc.close()
    print("los tokens de un pdf...")
    print(f"total_tokens: {total_tokens}")
    #print(f"prompt_tokens: {prompt_tokens}")
    #print(f"completion_tokens: {completion_tokens}")



    return all_words

@observe(name="extract_from_image", as_type="generation")
def extract_from_image(file_bytes: bytes) -> List[str]:
    base64_image = base64.b64encode(file_bytes).decode("utf-8")

    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0

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
    total_tokens += response.usage.total_tokens
    prompt_tokens += response.usage.prompt_tokens
    completion_tokens += response.usage.completion_tokens

    print("los tokens de una imagen...")
    print(f"total_tokens: {total_tokens}")
    #print(f"prompt_tokens: {prompt_tokens}")
    #print(f"completion_tokens: {completion_tokens}")

    config={"callbacks": [langfuse_handler]}

    return extract_words_from_text(text)
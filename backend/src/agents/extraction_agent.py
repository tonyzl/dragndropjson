import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
import io
from PIL import Image

# Pydantic Schema for structured output
from src.models import FormFields


# Load environment variables
load_dotenv()

# Initialize OpenAI client
client =os.getenv("OPENAI_API_KEY")


def encode_image(image_path: str) -> str:
    """Encode an image file as a base64 string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def extract_and_save_form_data(image_path: str)-> str:
    """Send image to LLM, parse structure, and save as a JSON file."""
    
    
    
    #image = Image.open(io.BytesIO(file_bytes))
    print("Encoding image...")
    base64_img = encode_image(image_path)
    
    
    print("Sending image to the LLM...")

    # Use the .parse() method to enforce structured output matching the Pydantic model
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": "Extract all text fields from this form image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_img}",
                            "detail": "high"
                        }
                    }
                ],
            }
        ],
        response_format=FormFields,
    )

    # Retrieve the parsed object
    form_data = completion.choices[0].message.parsed
    
    # Save to a JSON file
    print(f"Saving data to {output_json_path}...")
    
    with open(output_json_path, "w", encoding="utf-8") as f:
        # model_dump_json() creates a valid JSON string directly
        f.write(form_data.model_dump_json(indent=4))
        
    return form_data

if __name__ == "__main__":
    IMAGE_PATH = "sample_form.png"
    OUTPUT_FILE = "form_data.json"

    if not os.path.exists(IMAGE_PATH):
        print(f"Warning: Image not found at {IMAGE_PATH}. Please ensure the file exists.")
    else:
        try:
            result = extract_and_save_form_data(IMAGE_PATH, OUTPUT_FILE)
            print("\n--- Success! Data Saved ---")
            print(result.model_dump_json(indent=2))
        except Exception as e:
            print(f"An error occurred: {e}")
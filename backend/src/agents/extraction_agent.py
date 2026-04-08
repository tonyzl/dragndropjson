import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.models import ContractChangeOutput


from langfuse import observe


# Load environment variables
load_dotenv()


# Verificar que las API keys estén configuradas
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

@observe(name="extraction_agent", as_type="generation")
class ExtractionAgent:
    def __init__(self, model_name="gpt-4o"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        # Aquí es donde Pydantic se integra con el LLM
        self.structured_llm = self.llm.with_structured_output(ContractChangeOutput)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un Especialista en Auditoría Legal. Extrae cambios precisos en formato JSON."),
            ("human", "MAPA: {context_map}\n\nORIGINAL: {original_text}\n\nADENDA: {adenda_text}")
        ])

    def get_chain(self):
        return self.prompt | self.structured_llm
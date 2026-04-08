import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from langfuse import observe

# Load environment variables
load_dotenv()


# Verificar que las API keys estén configuradas
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

@observe(name="contextualization_agent", as_type="generation")
class ContextualizationAgent:
    def __init__(self, model_name="gpt-4o"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.prompt = ChatPromptTemplate.from_template("""
            Eres un Analista Legal Senior. Tu objetivo es mapear la estructura de dos documentos.
            
            CONTRATO ORIGINAL: {contrato_text}
            ADENDA: {adenda_text}
            
            Identifica qué secciones del contrato original están siendo afectadas por la adenda. 
            No extraigas cambios detallados aún, solo crea el mapa contextual.
        """)

    def get_chain(self):
        return self.prompt | self.llm
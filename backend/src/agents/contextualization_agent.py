from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

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
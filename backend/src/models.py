from pydantic import BaseModel, Field
from typing import List

class ContractChangeOutput(BaseModel):
    sections_changed: List[str] = Field(description="Lista de los nombres de las cláusulas que sufrieron cambios.")
    topics_touched: List[str] = Field(description="Categorías legales/comerciales afectadas.")
    summary_of_the_change: str = Field(description="Descripción detallada de los cambios encontrados con buena redaccion y sin acentos. Al final quiero un analisis profundo denominado 'CONCEPTO LEGAL' de las clausulas que sean abusivas o perjudiciales para alguna de las partes en mayusculas acorde a legislacion local inferida en los documentos, en el caso de que haya relacion entre los documentos")
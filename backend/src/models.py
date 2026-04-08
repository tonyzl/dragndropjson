from pydantic import BaseModel, Field
from typing import List

class ContractChangeOutput(BaseModel):
    sections_changed: List[str] = Field(description="Lista de los nombres de las cláusulas que sufrieron cambios.")
    topics_touched: List[str] = Field(description="Categorías legales/comerciales afectadas.")
    summary_of_the_change: str = Field(description="Descripción detallada de los cambios encontrados con buena redaccion y orden.")
from pydantic import BaseModel, Field


# Pydantic Schema for structured output
class FormFields(BaseModel):
    Nombre_Completo: str = Field(description="Nombre completo extraído del formulario.")
    Fecha_de_Nacimiento: str = Field(description="Fecha de nacimiento en formato YYYY-MM-DD si es posible.")
    Numero_de_Documento: str = Field(description="Número de documento o identificación encontrado.")
    Monto_Solicitado: str = Field(description="Monto solicitado en el formulario.")
    Firma: str = Field(description="Indicar 'Presente' o 'Ausente' según se detecte la firma.")
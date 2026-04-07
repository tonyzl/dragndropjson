"""
extraction_agent.py — Agente especializado en comparar y analizar el contenido de los mismos .


"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
import os
import math


class ExtractionAgent:
    def __init__(self):
        self.system_prompt = """
        Eres un Agente de Extracción de Diferencias Legales.
        Tu objetivo es identificar adiciones, eliminaciones y modificaciones específicas.
        Utiliza el 'Mapa de Correspondencia' del analista anterior y los textos originales.
        Debes responder EXCLUSIVAMENTE en formato JSON que cumpla con el esquema Pydantic definido.
        """

    def run(self, context_map, original_text, amendment_text, parent_trace):
        span = parent_trace.span(name="extraction_agent")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"CONTEXTO: {context_map}\n\nTEXTOS:\nOriginal: {original_text}\nAdenda: {amendment_text}"}
            ]
        )
        
        raw_json = response.choices[0].message.content
        # Validación Pydantic
        validated_data = ContractChangeOutput.model_validate_json(raw_json)
        
        span.end(output=validated_data.model_dump())
        return validated_data
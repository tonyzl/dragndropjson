"""
hr_agent.py — Agente especializado en Recursos Humanos.

Responde preguntas sobre:
- Políticas de vacaciones y permisos
- Beneficios corporativos
- Compensación y salarios
- Onboarding y offboarding
- Desempeño y desarrollo profesional
- Código de conducta
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
import os
import math
import json
from pathlib import Path


class ContextualizationAgent:
    def __init__(self):
        self.system_prompt = """
        Eres un Analista Legal Senior especializado en Estructura de Contratos.
        Tu tarea es recibir el texto de un contrato original y su adenda.
        Debes generar un 'Mapa de Correspondencia'. Identifica qué secciones se mantienen, 
        cuáles se mencionan en la adenda y cuál es el propósito de la modificación.
        No extraigas cambios detallados, solo mapea la estructura.
        """

    def run(self, original_text, amendment_text, parent_trace):
        span = parent_trace.span(name="contextualization_agent")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"CONTRATO ORIGINAL:\n{original_text}\n\nADENDA:\n{amendment_text}"}
            ]
        )
        result = response.choices[0].message.content
        span.end(output=result)
        return result
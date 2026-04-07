"""
orchestrator.py — Orquestador del sistema.

El orquestador:
1. Recibe los archivos
2. Dirige el flujo de trabajo usando GPT (routing LLM)
3. Activa al agente especializado correspondiente
4. Retorna la respuesta con metadatos de trazabilidad
"""

from __future__ import annotations
import os
import json
from typing import Dict, Any, Optional
from openai import OpenAI


ROUTING_SYSTEM_PROMPT = """Eres el orquestador para el sistema gestor de documentos.
Tu única tarea es coordinar a todos los agentes involucrados.



Responde ÚNICAMENTE con un objeto JSON con la siguiente estructura (sin markdown, sin texto adicional):
{

}
"""


class Orchestrator:
    """
    Orquestador central del sistema.
    
    Responsabilidades:
    - Gestionar el flujo de trabajo mediante un LLM de routing
    - 
    """

    def __init__(
        self,
        openai_client: OpenAI,
        contextualization_agent,
        extraction_agent,
        langfuse_client=None,
    ):
        self.client = openai_client
        self.agents = {
            "contextualization": contextualization_agent,
            "extraction": extraction_agent,
        }
        self.langfuse = langfuse_client
        self.routing_model = os.getenv("ROUTING_MODEL", "gpt-4o-mini")

    

    

   
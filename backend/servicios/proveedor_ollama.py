"""Proveedor de modelo con Ollama (Strategy concreta).

Implementa ProveedorModelo usando la API HTTP local de Ollama.
Cambiar de modelo = cambiar la variable de configuración 'modelo'.
"""

from __future__ import annotations

import httpx

from backend.dominio.interfaces import ProveedorModelo


class ProveedorOllama(ProveedorModelo):
    """Strategy concreta: conecta con Ollama local vía HTTP.

    Modelos soportados: qwen2.5:7b (Apache 2.0), llama3.2:3b (Meta).
    """

    def __init__(
        self,
        modelo: str = "qwen2.5:7b",
        url_base: str = "http://localhost:11434",
    ) -> None:
        self._modelo = modelo
        self._url_base = url_base

    def generar(self, prompt: str, contexto: str = "") -> str:
        """Genera texto llamando a la API de Ollama."""
        payload = {
            "model": self._modelo,
            "prompt": prompt,
            "stream": False,
        }
        if contexto:
            payload["system"] = contexto

        try:
            respuesta = httpx.post(
                f"{self._url_base}/api/generate",
                json=payload,
                timeout=90.0,
            )
            respuesta.raise_for_status()
            return respuesta.json().get("response", "")
        except (httpx.HTTPError, KeyError) as e:
            return f"[Error al generar con {self._modelo}: {e}]"

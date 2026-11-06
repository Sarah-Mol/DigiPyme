"""Configuración de DigiPyme.

Lee variables de entorno para el token del DENUE y el modelo.
El token se guarda en un archivo .env que no se sube al repositorio.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Cargar .env si existe
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)


class Config:
    """Configuración centralizada."""

    # DENUE
    DENUE_TOKEN: str = os.getenv("DENUE_TOKEN", "")

    # Modelo de IA (Strategy: cambiar aquí = cambiar modelo)
    MODELO_IA: str = os.getenv("MODELO_IA", "qwen2.5:7b")
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")

    # Rutas
    CATALOGO_APOYOS: str = os.getenv(
        "CATALOGO_APOYOS",
        str(Path(__file__).parent / "datos" / "catalogo_apoyos.json"),
    )
    CACHE_DENUE: str = os.getenv(
        "CACHE_DENUE",
        str(Path(__file__).parent / "datos" / "cache_denue"),
    )

    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

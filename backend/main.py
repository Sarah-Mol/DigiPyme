"""Punto de entrada de la API de DigiPyme (FastAPI).

Configura CORS, crea el orquestador y monta las rutas.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.rutas import router
from backend.config import Config
from backend.orquestador import Orquestador
from backend.servicios.adaptador_denue import AdaptadorDENUE, ProxyCacheDENUE
from backend.servicios.catalogo_apoyos_json import CatalogoApoyosJSON
from backend.servicios.proveedor_ollama import ProveedorOllama

app = FastAPI(
    title="DigiPyme API",
    description=(
        "Diagnóstico de digitalización para MIPYMES con agentes de IA. "
        "ODS 9: Industria, innovación e infraestructura."
    ),
    version="1.0.0",
)

# CORS para el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[Config.FRONTEND_URL, "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar rutas
app.include_router(router, prefix="/api")

# Orquestador (singleton por simplicidad en la demo)
_orquestador: Orquestador | None = None


def obtener_orquestador() -> Orquestador:
    """Crea o devuelve el orquestador configurado."""
    global _orquestador
    if _orquestador is None:
        proveedor = ProveedorOllama(
            modelo=Config.MODELO_IA,
            url_base=Config.OLLAMA_URL,
        )
        adaptador = AdaptadorDENUE(token=Config.DENUE_TOKEN)
        fuente = ProxyCacheDENUE(adaptador, ruta_cache=Config.CACHE_DENUE)
        catalogo = CatalogoApoyosJSON(ruta_archivo=Config.CATALOGO_APOYOS)
        _orquestador = Orquestador(proveedor, fuente, catalogo)
    return _orquestador


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

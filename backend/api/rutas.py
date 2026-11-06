"""Rutas de la API REST de DigiPyme (FastAPI).

POST /diagnostico  – Recibe el perfil y devuelve el diagnóstico completo.
GET  /reporte/{id} – Devuelve el PDF del reporte.
GET  /giros        – Lista los giros disponibles.
GET  /salud        – Health check.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.dominio.constantes import CATALOGO_GIROS, NOMBRES_PROCESOS, PROCESOS
from backend.dominio.entidades import (
    EvaluacionProceso,
    Giro,
    NivelMadurez,
    PerfilNegocio,
    Ubicacion,
)

router = APIRouter()

# Almacén temporal de reportes (sin base de datos, D-10)
_reportes: dict[str, str] = {}
_contador: int = 0


# ── Modelos de entrada/salida ──────────────────────────────────────────

class UbicacionIn(BaseModel):
    estado: str = Field(..., example="Jalisco")
    municipio: str = Field(..., example="San Pedro Tlaquepaque")
    clave_municipio: str = Field(..., example="14098")


class EvaluacionIn(BaseModel):
    proceso: str = Field(..., example="inventario")
    nivel: int = Field(..., ge=0, le=3, example=1)


class PerfilIn(BaseModel):
    giro: str = Field(..., example="abarrotes")
    tamano: str = Field(..., example="micro")
    ubicacion: UbicacionIn
    evaluaciones: list[EvaluacionIn]


class RecomendacionOut(BaseModel):
    proceso: str
    prioridad: float
    razon: str
    primer_paso: str
    fuente: str


class ApoyoOut(BaseModel):
    id_programa: str
    nombre: str
    dependencia: str
    beneficio: str
    requisitos: str
    vigencia: str
    url: str
    fecha_verificacion: str


class ResumenZonaOut(BaseModel):
    total_similares: int
    distribucion_tamano: dict[str, int]
    con_sitio_web: int
    con_correo: int
    texto_resumen: str


class DiagnosticoOut(BaseModel):
    reporte_id: str
    resumen_zona: ResumenZonaOut
    recomendaciones: list[RecomendacionOut]
    apoyos: list[ApoyoOut]
    fecha: str
    aviso: str


class GiroOut(BaseModel):
    clave: str
    nombre: str
    clase_scian: str


# ── Endpoints ──────────────────────────────────────────────────────────

@router.get("/salud")
async def salud() -> dict[str, str]:
    """Health check."""
    return {"estado": "ok", "servicio": "DigiPyme API"}


@router.get("/giros", response_model=list[GiroOut])
async def listar_giros() -> list[dict[str, str]]:
    """Lista los 6 giros disponibles del catálogo."""
    return [
        {"clave": clave, "nombre": giro.nombre, "clase_scian": giro.clase_scian}
        for clave, giro in CATALOGO_GIROS.items()
    ]


@router.get("/procesos")
async def listar_procesos() -> dict[str, str]:
    """Lista los 6 procesos que evalúa DigiPyme."""
    return NOMBRES_PROCESOS


@router.post("/diagnostico", response_model=DiagnosticoOut)
async def crear_diagnostico(perfil_in: PerfilIn) -> dict[str, Any]:
    """Recibe el perfil del negocio y devuelve el diagnóstico completo.

    Internamente llama al Orquestador (Façade), que coordina los 3 agentes.
    """
    # Validar giro
    if perfil_in.giro not in CATALOGO_GIROS:
        raise HTTPException(
            status_code=400,
            detail=f"Giro no válido. Opciones: {list(CATALOGO_GIROS.keys())}",
        )

    # Validar procesos
    for ev in perfil_in.evaluaciones:
        if ev.proceso not in PROCESOS:
            raise HTTPException(
                status_code=400,
                detail=f"Proceso no válido: {ev.proceso}. Opciones: {PROCESOS}",
            )

    # Construir entidades del dominio
    giro = CATALOGO_GIROS[perfil_in.giro]
    perfil = PerfilNegocio(
        giro=giro,
        tamano=perfil_in.tamano,
        ubicacion=Ubicacion(
            estado=perfil_in.ubicacion.estado,
            municipio=perfil_in.ubicacion.municipio,
            clave_municipio=perfil_in.ubicacion.clave_municipio,
        ),
        evaluaciones=[
            EvaluacionProceso(
                proceso=ev.proceso,
                nivel=NivelMadurez(ev.nivel),
            )
            for ev in perfil_in.evaluaciones
        ],
    )

    # Importar aquí para evitar circular imports y permitir lazy init
    from backend.main import obtener_orquestador

    orq = obtener_orquestador()
    diagnostico = orq.diagnosticar(perfil)

    # Generar reporte y guardarlo temporalmente
    global _contador
    _contador += 1
    reporte_id = f"rep-{_contador:04d}"
    _reportes[reporte_id] = orq.generar_reporte(diagnostico)

    return {
        "reporte_id": reporte_id,
        "resumen_zona": {
            "total_similares": diagnostico.resumen_zona.total_similares,
            "distribucion_tamano": diagnostico.resumen_zona.distribucion_tamano,
            "con_sitio_web": diagnostico.resumen_zona.con_sitio_web,
            "con_correo": diagnostico.resumen_zona.con_correo,
            "texto_resumen": diagnostico.resumen_zona.texto_resumen,
        },
        "recomendaciones": [
            {
                "proceso": r.proceso,
                "prioridad": r.prioridad,
                "razon": r.razon,
                "primer_paso": r.primer_paso,
                "fuente": r.fuente,
            }
            for r in diagnostico.recomendaciones
        ],
        "apoyos": [
            {
                "id_programa": a.id_programa,
                "nombre": a.nombre,
                "dependencia": a.dependencia,
                "beneficio": a.beneficio,
                "requisitos": a.requisitos,
                "vigencia": a.vigencia,
                "url": a.url,
                "fecha_verificacion": a.fecha_verificacion,
            }
            for a in diagnostico.apoyos
        ],
        "fecha": diagnostico.fecha,
        "aviso": diagnostico.aviso,
    }


@router.get("/reporte/{reporte_id}")
async def descargar_reporte(reporte_id: str) -> Any:
    """Devuelve el reporte HTML para descarga."""
    from fastapi.responses import HTMLResponse

    if reporte_id not in _reportes:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    return HTMLResponse(
        content=_reportes[reporte_id],
        headers={
            "Content-Disposition": f'attachment; filename="DigiPyme_Reporte_{reporte_id}.html"'
        },
    )

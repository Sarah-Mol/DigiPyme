"""Entidades del dominio de DigiPyme.

Cada entidad tiene una sola responsabilidad (SRP).
Las relaciones siguen la sección 4.1 del documento de visión.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional


class NivelMadurez(IntEnum):
    """Nivel de madurez digital de un proceso (escala 0–3)."""

    NO_SE_LLEVA = 0
    PAPEL = 1
    DIGITAL_AISLADO = 2
    DIGITAL_INTEGRADO = 3


@dataclass
class Giro:
    """Giro del catálogo de la demo con su clase SCIAN."""

    nombre: str
    clase_scian: str


@dataclass
class Ubicacion:
    """Estado y municipio con claves del INEGI."""

    estado: str
    municipio: str
    clave_municipio: str


@dataclass
class EvaluacionProceso:
    """Nivel de madurez de un proceso según las respuestas del cuestionario."""

    proceso: str
    nivel: NivelMadurez


@dataclass
class PerfilNegocio:
    """Describe el negocio: giro, tamaño, ubicación y procesos actuales.

    Compone una Ubicacion y varias EvaluacionProceso (composición).
    """

    giro: Giro
    tamano: str
    ubicacion: Ubicacion
    evaluaciones: list[EvaluacionProceso] = field(default_factory=list)


@dataclass
class ResumenZona:
    """Conteo de negocios similares en el municipio (salida del Agente de contexto)."""

    total_similares: int
    distribucion_tamano: dict[str, int] = field(default_factory=dict)
    con_sitio_web: int = 0
    con_correo: int = 0
    texto_resumen: str = ""


@dataclass
class Recomendacion:
    """Proceso a digitalizar con su prioridad y explicación."""

    proceso: str
    prioridad: float
    razon: str
    primer_paso: str
    fuente: str


@dataclass
class ProgramaApoyo:
    """Programa público del catálogo curado."""

    id_programa: str
    nombre: str
    dependencia: str
    beneficio: str
    requisitos: str
    vigencia: str
    url: str
    fecha_verificacion: str


@dataclass
class Diagnostico:
    """Conjunto ordenado de recomendaciones y apoyos.

    Agrega ProgramaApoyo (agregación): los programas existen
    independientemente del diagnóstico.
    """

    perfil: PerfilNegocio
    resumen_zona: ResumenZona
    recomendaciones: list[Recomendacion] = field(default_factory=list)
    apoyos: list[ProgramaApoyo] = field(default_factory=list)
    fecha: str = ""
    aviso: str = (
        "Este diagnóstico es orientativo. "
        "Confirma requisitos y fechas de los apoyos en la fuente oficial."
    )


@dataclass
class Reporte:
    """Documento final para el usuario (PDF)."""

    diagnostico: Diagnostico
    contenido_html: str = ""

    def generar_pdf(self) -> bytes:
        """Genera el PDF a partir del HTML. Se implementa con weasyprint o similar."""
        # Implementación simplificada para la demo
        return self.contenido_html.encode("utf-8")

"""Orquestador (patrón Façade).

Coordina el flujo de los tres agentes y el constructor de reporte.
La API llama diagnosticar(perfil) sin conocer a cada agente.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.agentes.agente_apoyos import AgenteApoyos
from backend.agentes.agente_contexto import AgenteContexto
from backend.agentes.agente_diagnostico import AgenteDiagnostico
from backend.dominio.constantes import CATALOGO_GIROS
from backend.dominio.entidades import Diagnostico, PerfilNegocio
from backend.dominio.interfaces import (
    CatalogoApoyos,
    FuenteUnidadesEconomicas,
    ProveedorModelo,
)
from backend.servicios.constructor_reporte import ConstructorReporte


class Orquestador:
    """Façade: un solo método diagnosticar(perfil) coordina todo.

    Composición: el orquestador "tiene" agentes y constructor.
    """

    def __init__(
        self,
        proveedor: ProveedorModelo,
        fuente_denue: FuenteUnidadesEconomicas,
        catalogo: CatalogoApoyos,
    ) -> None:
        self._agente_contexto = AgenteContexto(proveedor, fuente_denue)
        self._agente_diagnostico = AgenteDiagnostico(proveedor)
        self._agente_apoyos = AgenteApoyos(proveedor, catalogo)

    def diagnosticar(self, perfil: PerfilNegocio) -> Diagnostico:
        """Ejecuta el flujo completo: contexto → diagnóstico → apoyos → reporte."""

        # Buscar la clave del giro
        giro_clave = ""
        for clave, giro in CATALOGO_GIROS.items():
            if giro.clase_scian == perfil.giro.clase_scian:
                giro_clave = clave
                break

        # CU-2: Agente de contexto
        resultado_contexto = self._agente_contexto.ejecutar({
            "clave_municipio": perfil.ubicacion.clave_municipio,
            "clase_scian": perfil.giro.clase_scian,
            "giro_nombre": perfil.giro.nombre,
            "municipio_nombre": perfil.ubicacion.municipio,
        })
        resumen_zona = resultado_contexto["resumen_zona"]

        # CU-3: Agente de diagnóstico
        evaluaciones_dict = {
            e.proceso: e.nivel for e in perfil.evaluaciones
        }
        resultado_diagnostico = self._agente_diagnostico.ejecutar({
            "giro_clave": giro_clave,
            "giro_nombre": perfil.giro.nombre,
            "evaluaciones": evaluaciones_dict,
        })
        recomendaciones = resultado_diagnostico["recomendaciones"]

        # CU-4: Agente de apoyos
        procesos_top = [r.proceso for r in recomendaciones[:3]]
        resultado_apoyos = self._agente_apoyos.ejecutar({
            "estado": perfil.ubicacion.estado,
            "tamano": perfil.tamano,
            "procesos_recomendados": procesos_top,
            "giro_nombre": perfil.giro.nombre,
        })
        apoyos = resultado_apoyos["apoyos"]

        # Construir el diagnóstico
        diagnostico = Diagnostico(
            perfil=perfil,
            resumen_zona=resumen_zona,
            recomendaciones=recomendaciones,
            apoyos=apoyos,
            fecha=datetime.now().strftime("%d/%m/%Y %H:%M"),
        )

        return diagnostico

    def generar_reporte(self, diagnostico: Diagnostico) -> str:
        """CU-5: Genera el reporte HTML con el Builder."""
        constructor = ConstructorReporte(diagnostico)
        reporte = (
            constructor
            .con_portada()
            .con_resumen()
            .con_zona()
            .con_procesos()
            .con_apoyos()
            .con_fuentes()
            .construir()
        )
        return reporte.contenido_html

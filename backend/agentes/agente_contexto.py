"""Agente de contexto – Ubica al negocio frente a negocios similares.

Herramientas: API DENUE (Cuantificar, BuscarAreaActEstr) y modelo para
redactar el resumen. Las cifras salen siempre del DENUE; el modelo
solo redacta (sección 5.2 del documento de visión).
"""

from __future__ import annotations

from typing import Any

from backend.agentes.agente_base import Agente
from backend.dominio.entidades import ResumenZona
from backend.dominio.interfaces import FuenteUnidadesEconomicas, ProveedorModelo


class AgenteContexto(Agente):
    """Agente que consulta el DENUE para resumir la zona del negocio.

    Usa composición: "tiene" una fuente de unidades económicas (DIP)
    y un proveedor de modelo (Strategy).
    """

    def __init__(
        self,
        proveedor: ProveedorModelo,
        fuente: FuenteUnidadesEconomicas,
    ) -> None:
        super().__init__(proveedor)
        self._fuente = fuente

    def recolectar(self, entrada: dict[str, Any]) -> dict[str, Any]:
        """Consulta el DENUE con la clase SCIAN y la clave del municipio."""
        clave_municipio = entrada["clave_municipio"]
        clase_scian = entrada["clase_scian"]

        total = self._fuente.cuantificar(clave_municipio, clase_scian)
        establecimientos = self._fuente.buscar_area(clave_municipio, clase_scian)

        # Clasificar por tamaño y presencia digital
        distribucion: dict[str, int] = {}
        con_sitio = 0
        con_correo = 0

        for est in establecimientos:
            estrato = est.get("Estrato", "Sin dato")
            distribucion[estrato] = distribucion.get(estrato, 0) + 1
            if est.get("Sitio_internet", "").strip():
                con_sitio += 1
            if est.get("Correo_e", "").strip():
                con_correo += 1

        return {
            "total": total,
            "distribucion": distribucion,
            "con_sitio_web": con_sitio,
            "con_correo": con_correo,
            "giro_nombre": entrada.get("giro_nombre", ""),
            "municipio_nombre": entrada.get("municipio_nombre", ""),
        }

    def razonar(self, datos: dict[str, Any]) -> dict[str, Any]:
        """El modelo redacta el resumen en lenguaje sencillo."""
        prompt = (
            f"Redacta un párrafo breve para el dueño de un negocio de "
            f"{datos['giro_nombre']} en {datos['municipio_nombre']}. "
            f"En su municipio hay {datos['total']} negocios del mismo giro. "
            f"Distribución por tamaño: {datos['distribucion']}. "
            f"{datos['con_sitio_web']} tienen sitio web y "
            f"{datos['con_correo']} tienen correo registrado. "
            f"Usa lenguaje sencillo, sin términos técnicos. "
            f"Máximo 3 oraciones de 25 palabras o menos cada una."
        )
        texto = self._proveedor.generar(prompt)
        datos["texto_resumen"] = texto
        return datos

    def validar(self, resultado: dict[str, Any]) -> dict[str, Any]:
        """Verifica que el resumen tenga contenido."""
        if not resultado.get("texto_resumen"):
            resultado["texto_resumen"] = (
                f"En tu municipio hay {resultado['total']} negocios "
                f"de tu mismo giro registrados en el DENUE."
            )

        return {
            "resumen_zona": ResumenZona(
                total_similares=resultado["total"],
                distribucion_tamano=resultado["distribucion"],
                con_sitio_web=resultado["con_sitio_web"],
                con_correo=resultado["con_correo"],
                texto_resumen=resultado["texto_resumen"],
            )
        }

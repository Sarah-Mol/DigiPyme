"""Catálogo de apoyos en JSON (implementación concreta de CatalogoApoyos).

Lee un archivo JSON con los programas de apoyo verificados.
Filtra por estado, tamaño y procesos relevantes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from backend.dominio.entidades import ProgramaApoyo
from backend.dominio.interfaces import CatalogoApoyos


class CatalogoApoyosJSON(CatalogoApoyos):
    """Implementación que lee programas de apoyo desde un archivo JSON.

    Programa a una interfaz (DIP): los agentes no saben que es un JSON.
    Agregar un programa = modificar solo el archivo JSON (OCP).
    """

    def __init__(self, ruta_archivo: str = "backend/datos/catalogo_apoyos.json") -> None:
        self._ruta = Path(ruta_archivo)
        self._programas: list[ProgramaApoyo] = []
        self._cargar()

    def _cargar(self) -> None:
        """Carga los programas del archivo JSON."""
        if not self._ruta.exists():
            return

        with open(self._ruta, encoding="utf-8") as f:
            datos = json.load(f)

        for item in datos:
            self._programas.append(
                ProgramaApoyo(
                    id_programa=item["id_programa"],
                    nombre=item["nombre"],
                    dependencia=item["dependencia"],
                    beneficio=item["beneficio"],
                    requisitos=item["requisitos"],
                    vigencia=item["vigencia"],
                    url=item["url"],
                    fecha_verificacion=item["fecha_verificacion"],
                )
            )

    def filtrar(
        self, estado: str, tamano: str, procesos: list[str]
    ) -> list[ProgramaApoyo]:
        """Filtra programas por estado, tamaño y procesos relevantes."""
        # En la versión de la demo, todos los programas son para
        # Jalisco y MIPYMES, así que el filtro principal es por vigencia
        resultado = []
        for programa in self._programas:
            # Incluir programas vigentes o con convocatoria por confirmar
            if "cerrada" not in programa.vigencia.lower() or \
               "por confirmar" in programa.vigencia.lower():
                resultado.append(programa)
            elif "cerrada" in programa.vigencia.lower():
                # Incluir con nota de próxima convocatoria
                resultado.append(programa)
        return resultado

    def obtener_por_id(self, id_programa: str) -> Optional[ProgramaApoyo]:
        """Obtiene un programa por su identificador."""
        for programa in self._programas:
            if programa.id_programa == id_programa:
                return programa
        return None

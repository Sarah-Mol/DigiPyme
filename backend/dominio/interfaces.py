"""Interfaces (contratos) del dominio de DigiPyme.

Los agentes dependen de estas interfaces, no de implementaciones concretas (DIP).
Cualquier implementación que cumpla el contrato puede sustituir a otra sin romper
el programa (LSP).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from .entidades import ProgramaApoyo


class ProveedorModelo(ABC):
    """Interfaz Strategy para el modelo de IA.

    Cambiar de modelo = cambiar la implementación concreta por configuración.
    Los agentes nunca saben qué modelo están usando (0 líneas al cambiar).
    """

    @abstractmethod
    def generar(self, prompt: str, contexto: str = "") -> str:
        """Genera texto a partir de un prompt y contexto opcional."""
        ...


class FuenteUnidadesEconomicas(ABC):
    """Interfaz para la fuente de datos de unidades económicas.

    Permite que el Agente de contexto funcione con la API del DENUE,
    con una descarga masiva o con datos de prueba (DIP).
    """

    @abstractmethod
    def cuantificar(self, clave_municipio: str, clase_scian: str) -> int:
        """Cuenta unidades económicas por municipio y clase SCIAN."""
        ...

    @abstractmethod
    def buscar_area(
        self, clave_municipio: str, clase_scian: str
    ) -> list[dict]:
        """Busca establecimientos en un área por actividad económica."""
        ...


class CatalogoApoyos(ABC):
    """Interfaz para el catálogo de programas de apoyo.

    La versión inicial lee un JSON; una futura podría consultar una base
    de datos o una API (OCP, DIP).
    """

    @abstractmethod
    def filtrar(
        self, estado: str, tamano: str, procesos: list[str]
    ) -> list[ProgramaApoyo]:
        """Filtra programas por estado, tamaño del negocio y procesos."""
        ...

    @abstractmethod
    def obtener_por_id(self, id_programa: str) -> Optional[ProgramaApoyo]:
        """Obtiene un programa por su identificador."""
        ...

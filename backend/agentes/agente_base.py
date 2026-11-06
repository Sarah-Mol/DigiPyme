"""Clase abstracta Agente con el patrón Template Method.

El método ejecutar() define el algoritmo:
  recolectar() → razonar() → validar()

Las subclases implementan cada paso. Todo agente valida su salida
antes de entregarla (sección 4.2 del documento de visión).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from backend.dominio.interfaces import ProveedorModelo


class Agente(ABC):
    """Clase abstracta que implementa el patrón Template Method.

    Cada agente "tiene" un proveedor de modelo (composición),
    lo que permite cambiar de modelo sin tocar al agente (Strategy + DIP).
    """

    def __init__(self, proveedor: ProveedorModelo) -> None:
        self._proveedor = proveedor

    def ejecutar(self, entrada: dict[str, Any]) -> dict[str, Any]:
        """Método plantilla: recolectar → razonar → validar.

        Este método NO se sobreescribe. Las subclases implementan
        los tres pasos abstractos.
        """
        datos = self.recolectar(entrada)
        resultado = self.razonar(datos)
        return self.validar(resultado)

    @abstractmethod
    def recolectar(self, entrada: dict[str, Any]) -> dict[str, Any]:
        """Obtiene los datos necesarios de las fuentes."""
        ...

    @abstractmethod
    def razonar(self, datos: dict[str, Any]) -> dict[str, Any]:
        """Aplica reglas y/o usa el modelo para generar la salida."""
        ...

    @abstractmethod
    def validar(self, resultado: dict[str, Any]) -> dict[str, Any]:
        """Valida formato y contenido de la salida."""
        ...

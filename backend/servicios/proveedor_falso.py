"""Proveedor de modelo falso para pruebas (Strategy concreta / LSP).

Implementa ProveedorModelo con respuestas predefinidas.
Demuestra LSP: cualquier implementación que cumpla el contrato
puede sustituir a otra sin romper el programa.
"""

from __future__ import annotations

from backend.dominio.interfaces import ProveedorModelo


class ProveedorFalso(ProveedorModelo):
    """Strategy de prueba: devuelve respuestas predefinidas.

    Útil para pruebas unitarias sin depender de Ollama.
    """

    def __init__(self, respuestas: dict[str, str] | None = None) -> None:
        self._respuestas = respuestas or {}
        self._respuesta_default = '[]'
        self._llamadas: list[str] = []

    def generar(self, prompt: str, contexto: str = "") -> str:
        """Devuelve una respuesta predefinida según palabras clave del prompt."""
        self._llamadas.append(prompt)

        # Buscar coincidencia por palabra clave
        for clave, respuesta in self._respuestas.items():
            if clave.lower() in prompt.lower():
                return respuesta

        return self._respuesta_default

    @property
    def llamadas(self) -> list[str]:
        """Permite verificar qué prompts se enviaron en las pruebas."""
        return self._llamadas

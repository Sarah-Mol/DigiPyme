"""Agente de apoyos – Propone programas públicos aplicables.

Cómo evita inventar programas (D-9):
1. Filtra el catálogo con reglas (estado, tamaño, procesos).
2. El modelo solo recibe los programas filtrados y responde con IDs.
3. El validador descarta cualquier ID que no exista en el catálogo.
"""

from __future__ import annotations

import json
from typing import Any

from backend.agentes.agente_base import Agente
from backend.dominio.entidades import ProgramaApoyo
from backend.dominio.interfaces import CatalogoApoyos, ProveedorModelo


class AgenteApoyos(Agente):
    """Agente que recomienda programas de apoyo del catálogo curado.

    Usa composición: "tiene" un catálogo de apoyos (DIP) y un proveedor
    de modelo (Strategy).
    """

    def __init__(
        self,
        proveedor: ProveedorModelo,
        catalogo: CatalogoApoyos,
    ) -> None:
        super().__init__(proveedor)
        self._catalogo = catalogo

    def recolectar(self, entrada: dict[str, Any]) -> dict[str, Any]:
        """Filtra el catálogo con reglas: estado, tamaño, procesos recomendados."""
        estado = entrada.get("estado", "Jalisco")
        tamano = entrada.get("tamano", "micro")
        procesos = entrada.get("procesos_recomendados", [])

        candidatos = self._catalogo.filtrar(estado, tamano, procesos)
        return {
            "candidatos": candidatos,
            "giro_nombre": entrada.get("giro_nombre", ""),
            "procesos": procesos,
        }

    def razonar(self, datos: dict[str, Any]) -> dict[str, Any]:
        """El modelo elige 1 a 3 programas del catálogo; solo puede responder con IDs."""
        candidatos = datos["candidatos"]

        if not candidatos:
            datos["ids_seleccionados"] = []
            return datos

        lista = "\n".join(
            f"- ID: {p.id_programa} | {p.nombre}: {p.beneficio} "
            f"(vigencia: {p.vigencia})"
            for p in candidatos
        )

        prompt = (
            f"Eres un asesor para un negocio de {datos['giro_nombre']}. "
            f"Los procesos que más necesita digitalizar son: "
            f"{', '.join(datos['procesos'])}.\n\n"
            f"Estos son los programas de apoyo disponibles:\n{lista}\n\n"
            f"Elige de 1 a 3 programas que mejor apliquen. "
            f"Responde SOLO con un JSON: [\"ID1\", \"ID2\"]. "
            f"NO inventes IDs; usa SOLO los de la lista."
        )

        respuesta = self._proveedor.generar(prompt)
        datos["respuesta_modelo"] = respuesta
        return datos

    def validar(self, resultado: dict[str, Any]) -> dict[str, Any]:
        """Descarta cualquier ID que no exista en el catálogo."""
        respuesta = resultado.get("respuesta_modelo", "")
        candidatos = resultado["candidatos"]

        apoyos_validos: list[ProgramaApoyo] = []

        if not candidatos:
            return {"apoyos": apoyos_validos}

        # Parsear IDs del modelo
        try:
            texto = respuesta.strip()
            if texto.startswith("```"):
                texto = texto.split("\n", 1)[1] if "\n" in texto else texto
            if texto.endswith("```"):
                texto = texto.rsplit("```", 1)[0]
            texto = texto.strip()
            if texto.startswith("json"):
                texto = texto[4:].strip()

            ids = json.loads(texto)
            if isinstance(ids, list):
                for id_prog in ids[:3]:  # Máximo 3
                    programa = self._catalogo.obtener_por_id(str(id_prog))
                    if programa is not None:
                        apoyos_validos.append(programa)
        except (json.JSONDecodeError, AttributeError):
            # Si el modelo no generó JSON válido, usar los primeros candidatos
            apoyos_validos = candidatos[:3]

        # Si no se encontró nada válido pero hay candidatos, usar los primeros
        if not apoyos_validos and candidatos:
            apoyos_validos = candidatos[:2]

        return {"apoyos": apoyos_validos}

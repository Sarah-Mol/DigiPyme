"""Agente de diagnóstico – Decide qué procesos digitalizar primero.

Fórmula de prioridad (código, no modelo):
  prioridad = (3 − nivel_actual) × impacto_del_proceso_para_el_giro

El modelo solo redacta la razón y el primer paso (D-8).
Un validador revisa formato y procesos existentes.
"""

from __future__ import annotations

import json
from typing import Any

from backend.agentes.agente_base import Agente
from backend.dominio.constantes import (
    IMPACTO_POR_GIRO,
    NOMBRES_PROCESOS,
    PROCESOS,
)
from backend.dominio.entidades import NivelMadurez, Recomendacion
from backend.dominio.interfaces import ProveedorModelo


class AgenteDiagnostico(Agente):
    """Agente que prioriza procesos a digitalizar.

    Separación reglas/modelo: las reglas calculan puntuaciones (código);
    el modelo solo explica y redacta.
    """

    def __init__(self, proveedor: ProveedorModelo) -> None:
        super().__init__(proveedor)

    def recolectar(self, entrada: dict[str, Any]) -> dict[str, Any]:
        """Obtiene evaluaciones del perfil y la tabla de impacto del giro."""
        giro_clave = entrada["giro_clave"]
        evaluaciones = entrada["evaluaciones"]  # dict[str, int]
        impactos = IMPACTO_POR_GIRO.get(giro_clave, {})

        # Calcular prioridad con código
        priorizados = []
        for proceso in PROCESOS:
            nivel = evaluaciones.get(proceso, 0)
            impacto = impactos.get(proceso, 1)
            brecha = NivelMadurez.DIGITAL_INTEGRADO - nivel  # 3 - nivel
            prioridad = brecha * impacto
            priorizados.append({
                "proceso": proceso,
                "nombre": NOMBRES_PROCESOS[proceso],
                "nivel_actual": nivel,
                "impacto": impacto,
                "brecha": brecha,
                "prioridad": prioridad,
            })

        # Ordenar por prioridad descendente
        priorizados.sort(key=lambda x: x["prioridad"], reverse=True)

        return {
            "priorizados": priorizados,
            "giro_nombre": entrada.get("giro_nombre", ""),
        }

    def razonar(self, datos: dict[str, Any]) -> dict[str, Any]:
        """El modelo redacta la razón y el primer paso de cada recomendación."""
        priorizados = datos["priorizados"]
        giro = datos["giro_nombre"]

        lista_procesos = "\n".join(
            f"- {p['nombre']}: nivel actual {p['nivel_actual']}/3, "
            f"prioridad {p['prioridad']}"
            for p in priorizados
        )

        prompt = (
            f"Eres un asesor de digitalización para un negocio de {giro}. "
            f"Estos son sus procesos ordenados por prioridad:\n{lista_procesos}\n\n"
            f"Para cada proceso, escribe un JSON con esta estructura:\n"
            f'[{{"proceso": "nombre", "razon": "por qué importa (1 oración)", '
            f'"primer_paso": "acción concreta y de bajo costo (1 oración)"}}]\n\n'
            f"Usa lenguaje sencillo, sin términos técnicos. "
            f"Responde SOLO con el JSON, sin texto adicional."
        )

        respuesta = self._proveedor.generar(prompt)
        datos["respuesta_modelo"] = respuesta
        return datos

    def validar(self, resultado: dict[str, Any]) -> dict[str, Any]:
        """Valida formato JSON y que solo mencione procesos existentes."""
        priorizados = resultado["priorizados"]
        respuesta = resultado.get("respuesta_modelo", "")

        recomendaciones = []
        explicaciones = {}

        # Intentar parsear la respuesta del modelo
        try:
            # Limpiar posibles marcadores de código
            texto = respuesta.strip()
            if texto.startswith("```"):
                texto = texto.split("\n", 1)[1] if "\n" in texto else texto
            if texto.endswith("```"):
                texto = texto.rsplit("```", 1)[0]
            texto = texto.strip()
            if texto.startswith("json"):
                texto = texto[4:].strip()

            items = json.loads(texto)
            if isinstance(items, list):
                for item in items:
                    nombre = item.get("proceso", "")
                    # Verificar que el proceso existe
                    if nombre in NOMBRES_PROCESOS.values():
                        explicaciones[nombre] = {
                            "razon": item.get("razon", ""),
                            "primer_paso": item.get("primer_paso", ""),
                        }
        except (json.JSONDecodeError, AttributeError):
            pass  # Usaremos textos de respaldo

        # Construir recomendaciones con datos de las reglas
        for p in priorizados:
            nombre = p["nombre"]
            expl = explicaciones.get(nombre, {})
            razon = expl.get("razon", "")
            primer_paso = expl.get("primer_paso", "")

            # Texto de respaldo si el modelo no generó algo válido
            if not razon:
                razon = (
                    f"Tu {nombre.lower()} tiene un nivel de madurez "
                    f"{p['nivel_actual']} de 3 y es importante para tu giro."
                )
            if not primer_paso:
                primer_paso = (
                    f"Busca una herramienta gratuita o de bajo costo "
                    f"para mejorar tu {nombre.lower()}."
                )

            recomendaciones.append(
                Recomendacion(
                    proceso=nombre,
                    prioridad=p["prioridad"],
                    razon=razon,
                    primer_paso=primer_paso,
                    fuente=f"Regla: brecha ({p['brecha']}) × impacto ({p['impacto']})",
                )
            )

        return {"recomendaciones": recomendaciones}

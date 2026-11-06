"""Pruebas del Agente de apoyos con proveedor falso.

Verifica que no invente programas (D-9):
- Solo devuelve IDs del catálogo.
- Descarta IDs inexistentes.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.agentes.agente_apoyos import AgenteApoyos
from backend.dominio.entidades import ProgramaApoyo
from backend.dominio.interfaces import CatalogoApoyos
from backend.servicios.proveedor_falso import ProveedorFalso
from typing import Optional


class CatalogoFalso(CatalogoApoyos):
    """Catálogo falso para pruebas."""

    def __init__(self) -> None:
        self._programas = [
            ProgramaApoyo(
                id_programa="SE-PAGOS-2026",
                nombre="Crece tu Mipyme con pagos digitales",
                dependencia="Secretaría de Economía",
                beneficio="Terminales de pago digital",
                requisitos="Ser MIPYME",
                vigencia="Activo",
                url="https://ejemplo.com",
                fecha_verificacion="4 nov 2026",
            ),
            ProgramaApoyo(
                id_programa="SAT-CFDI-40",
                nombre="Facturación CFDI 4.0",
                dependencia="SAT",
                beneficio="Facturas gratis",
                requisitos="RFC",
                vigencia="Permanente",
                url="https://sat.gob.mx",
                fecha_verificacion="4 nov 2026",
            ),
        ]

    def filtrar(self, estado: str, tamano: str, procesos: list[str]) -> list[ProgramaApoyo]:
        return self._programas

    def obtener_por_id(self, id_programa: str) -> Optional[ProgramaApoyo]:
        for p in self._programas:
            if p.id_programa == id_programa:
                return p
        return None


def test_selecciona_ids_validos():
    """El agente debe devolver solo programas con IDs del catálogo."""
    respuesta = json.dumps(["SE-PAGOS-2026", "SAT-CFDI-40"])
    proveedor = ProveedorFalso(respuestas={"Elige": respuesta})
    catalogo = CatalogoFalso()
    agente = AgenteApoyos(proveedor, catalogo)

    resultado = agente.ejecutar({
        "estado": "Jalisco",
        "tamano": "micro",
        "procesos_recomendados": ["Ventas y cobro"],
        "giro_nombre": "Abarrotes",
    })

    apoyos = resultado["apoyos"]
    assert len(apoyos) == 2
    ids = {a.id_programa for a in apoyos}
    assert "SE-PAGOS-2026" in ids
    assert "SAT-CFDI-40" in ids
    print("✓ test_selecciona_ids_validos")


def test_descarta_ids_inventados():
    """IDs que no existan en el catálogo deben descartarse (D-9)."""
    respuesta = json.dumps(["SE-PAGOS-2026", "INVENTADO-123", "NO-EXISTE"])
    proveedor = ProveedorFalso(respuestas={"Elige": respuesta})
    catalogo = CatalogoFalso()
    agente = AgenteApoyos(proveedor, catalogo)

    resultado = agente.ejecutar({
        "estado": "Jalisco",
        "tamano": "micro",
        "procesos_recomendados": ["Ventas y cobro"],
        "giro_nombre": "Abarrotes",
    })

    apoyos = resultado["apoyos"]
    # Solo debe devolver SE-PAGOS-2026 (el único válido)
    assert len(apoyos) == 1
    assert apoyos[0].id_programa == "SE-PAGOS-2026"
    print("✓ test_descarta_ids_inventados")


def test_cero_programas_inventados():
    """Nunca debe haber 0 programas fuera del catálogo en la salida."""
    respuesta = json.dumps(["FAKE-1", "FAKE-2", "FAKE-3"])
    proveedor = ProveedorFalso(respuestas={"Elige": respuesta})
    catalogo = CatalogoFalso()
    agente = AgenteApoyos(proveedor, catalogo)

    resultado = agente.ejecutar({
        "estado": "Jalisco",
        "tamano": "micro",
        "procesos_recomendados": ["Inventario"],
        "giro_nombre": "Ferretería",
    })

    apoyos = resultado["apoyos"]
    # Debe usar fallback: primeros candidatos del catálogo
    for a in apoyos:
        assert catalogo.obtener_por_id(a.id_programa) is not None
    print("✓ test_cero_programas_inventados")


if __name__ == "__main__":
    test_selecciona_ids_validos()
    test_descarta_ids_inventados()
    test_cero_programas_inventados()
    print("\nTodas las pruebas del Agente de apoyos pasaron.")

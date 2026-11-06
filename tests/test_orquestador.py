"""Pruebas del Orquestador (Façade) con componentes falsos."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.dominio.entidades import (
    EvaluacionProceso,
    Giro,
    NivelMadurez,
    PerfilNegocio,
    ProgramaApoyo,
    Ubicacion,
)
from backend.dominio.interfaces import CatalogoApoyos, FuenteUnidadesEconomicas
from backend.orquestador import Orquestador
from backend.servicios.proveedor_falso import ProveedorFalso
from typing import Optional


class FuenteFalsa(FuenteUnidadesEconomicas):
    def cuantificar(self, clave_municipio: str, clase_scian: str) -> int:
        return 100

    def buscar_area(self, clave_municipio: str, clase_scian: str) -> list[dict]:
        return [{"Estrato": "0 a 5 personas", "Sitio_internet": "", "Correo_e": ""}]


class CatalogoFalso(CatalogoApoyos):
    def __init__(self) -> None:
        self._p = ProgramaApoyo(
            id_programa="TEST-1",
            nombre="Programa Test",
            dependencia="Test",
            beneficio="Beneficio",
            requisitos="Ninguno",
            vigencia="Activo",
            url="https://test.com",
            fecha_verificacion="2026-11-04",
        )

    def filtrar(self, estado: str, tamano: str, procesos: list[str]) -> list[ProgramaApoyo]:
        return [self._p]

    def obtener_por_id(self, id_programa: str) -> Optional[ProgramaApoyo]:
        return self._p if id_programa == "TEST-1" else None


def test_flujo_completo():
    """El orquestador debe coordinar los 3 agentes y devolver un diagnóstico."""
    respuestas_modelo = {
        "Redacta": "En tu zona hay negocios similares.",
        "asesor": json.dumps([
            {"proceso": "Ventas y cobro", "razon": "Es clave.", "primer_paso": "Pide terminal."},
        ]),
        "Elige": json.dumps(["TEST-1"]),
    }
    proveedor = ProveedorFalso(respuestas=respuestas_modelo)
    fuente = FuenteFalsa()
    catalogo = CatalogoFalso()

    orq = Orquestador(proveedor, fuente, catalogo)

    perfil = PerfilNegocio(
        giro=Giro(nombre="Abarrotes", clase_scian="461110"),
        tamano="micro",
        ubicacion=Ubicacion(
            estado="Jalisco",
            municipio="San Pedro Tlaquepaque",
            clave_municipio="14098",
        ),
        evaluaciones=[
            EvaluacionProceso("inventario", NivelMadurez.PAPEL),
            EvaluacionProceso("ventas_cobro", NivelMadurez.NO_SE_LLEVA),
            EvaluacionProceso("facturacion_electronica", NivelMadurez.NO_SE_LLEVA),
            EvaluacionProceso("cobranza_clientes", NivelMadurez.DIGITAL_AISLADO),
            EvaluacionProceso("atencion_presencia_digital", NivelMadurez.PAPEL),
            EvaluacionProceso("compras_proveedores", NivelMadurez.PAPEL),
        ],
    )

    diagnostico = orq.diagnosticar(perfil)

    # Verificar estructura del diagnóstico
    assert diagnostico.resumen_zona.total_similares == 100
    assert len(diagnostico.recomendaciones) == 6
    assert diagnostico.recomendaciones[0].prioridad >= diagnostico.recomendaciones[-1].prioridad
    assert len(diagnostico.apoyos) >= 1
    assert diagnostico.aviso != ""
    assert diagnostico.fecha != ""
    print("✓ test_flujo_completo")


def test_reporte_html():
    """El orquestador debe generar HTML del reporte con el Builder."""
    proveedor = ProveedorFalso(respuestas={
        "Redacta": "Resumen de zona.",
        "asesor": "[]",
        "Elige": "[]",
    })
    fuente = FuenteFalsa()
    catalogo = CatalogoFalso()
    orq = Orquestador(proveedor, fuente, catalogo)

    perfil = PerfilNegocio(
        giro=Giro(nombre="Estética", clase_scian="812110"),
        tamano="micro",
        ubicacion=Ubicacion(estado="Jalisco", municipio="Guadalajara", clave_municipio="14039"),
        evaluaciones=[
            EvaluacionProceso("inventario", NivelMadurez.NO_SE_LLEVA),
            EvaluacionProceso("ventas_cobro", NivelMadurez.PAPEL),
            EvaluacionProceso("facturacion_electronica", NivelMadurez.NO_SE_LLEVA),
            EvaluacionProceso("cobranza_clientes", NivelMadurez.NO_SE_LLEVA),
            EvaluacionProceso("atencion_presencia_digital", NivelMadurez.NO_SE_LLEVA),
            EvaluacionProceso("compras_proveedores", NivelMadurez.PAPEL),
        ],
    )

    diagnostico = orq.diagnosticar(perfil)
    html = orq.generar_reporte(diagnostico)

    assert "DigiPyme" in html
    assert "orientativo" in html
    assert "Estética" in html
    print("✓ test_reporte_html")


if __name__ == "__main__":
    test_flujo_completo()
    test_reporte_html()
    print("\nTodas las pruebas del Orquestador pasaron.")

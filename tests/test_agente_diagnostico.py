"""Pruebas del Agente de diagnóstico con proveedor falso."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.agentes.agente_diagnostico import AgenteDiagnostico
from backend.servicios.proveedor_falso import ProveedorFalso


def test_prioridad_formula():
    """La prioridad debe ser (3 - nivel) × impacto, calculada por código."""
    respuesta_json = json.dumps([
        {"proceso": "Ventas y cobro", "razon": "Cobrar en efectivo limita tus ventas.", "primer_paso": "Pide una terminal de pago."},
        {"proceso": "Inventario", "razon": "Una libreta es difícil de consultar.", "primer_paso": "Usa una hoja de cálculo."},
        {"proceso": "Facturación electrónica", "razon": "Sin facturas pierdes clientes.", "primer_paso": "Registra tu RFC en el SAT."},
        {"proceso": "Compras a proveedores", "razon": "Ordenar por WhatsApp puede causar errores.", "primer_paso": "Haz una lista en hoja de cálculo."},
        {"proceso": "Atención y presencia digital", "razon": "Más personas te encontrarán.", "primer_paso": "Crea un perfil en Google Maps."},
        {"proceso": "Cobranza a clientes", "razon": "Llevar cuenta de quién te debe.", "primer_paso": "Registra cada venta fiada."},
    ])

    proveedor = ProveedorFalso(respuestas={"asesor": respuesta_json})
    agente = AgenteDiagnostico(proveedor)

    resultado = agente.ejecutar({
        "giro_clave": "abarrotes",
        "giro_nombre": "Abarrotes",
        "evaluaciones": {
            "inventario": 1,          # brecha=2, impacto=3 → 6
            "ventas_cobro": 0,         # brecha=3, impacto=3 → 9
            "facturacion_electronica": 0,  # brecha=3, impacto=2 → 6
            "cobranza_clientes": 2,    # brecha=1, impacto=1 → 1
            "atencion_presencia_digital": 1,  # brecha=2, impacto=2 → 4
            "compras_proveedores": 1,  # brecha=2, impacto=3 → 6
        },
    })

    recs = resultado["recomendaciones"]
    assert len(recs) == 6
    # Ventas y cobro debe ser la primera (prioridad 9)
    assert recs[0].proceso == "Ventas y cobro"
    assert recs[0].prioridad == 9
    # Cobranza debe ser la última (prioridad 1)
    assert recs[-1].proceso == "Cobranza a clientes"
    assert recs[-1].prioridad == 1
    print("✓ test_prioridad_formula")


def test_texto_respaldo_si_modelo_falla():
    """Si el modelo no genera JSON válido, debe usar texto de respaldo."""
    proveedor = ProveedorFalso(respuestas={"asesor": "no soy un JSON válido"})
    agente = AgenteDiagnostico(proveedor)

    resultado = agente.ejecutar({
        "giro_clave": "abarrotes",
        "giro_nombre": "Abarrotes",
        "evaluaciones": {
            "inventario": 1,
            "ventas_cobro": 0,
            "facturacion_electronica": 0,
            "cobranza_clientes": 2,
            "atencion_presencia_digital": 1,
            "compras_proveedores": 1,
        },
    })

    recs = resultado["recomendaciones"]
    assert len(recs) == 6
    # Debe tener texto de respaldo, no vacío
    for r in recs:
        assert len(r.razon) > 0
        assert len(r.primer_paso) > 0
    print("✓ test_texto_respaldo_si_modelo_falla")


def test_proceso_nivel3_prioridad_cero():
    """Un proceso ya digital e integrado (nivel 3) debe tener prioridad 0."""
    proveedor = ProveedorFalso(respuestas={"asesor": "[]"})
    agente = AgenteDiagnostico(proveedor)

    resultado = agente.ejecutar({
        "giro_clave": "abarrotes",
        "giro_nombre": "Abarrotes",
        "evaluaciones": {
            "inventario": 3,
            "ventas_cobro": 3,
            "facturacion_electronica": 3,
            "cobranza_clientes": 3,
            "atencion_presencia_digital": 3,
            "compras_proveedores": 3,
        },
    })

    for r in resultado["recomendaciones"]:
        assert r.prioridad == 0
    print("✓ test_proceso_nivel3_prioridad_cero")


if __name__ == "__main__":
    test_prioridad_formula()
    test_texto_respaldo_si_modelo_falla()
    test_proceso_nivel3_prioridad_cero()
    print("\nTodas las pruebas del Agente de diagnóstico pasaron.")

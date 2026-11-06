"""Pruebas del Agente de contexto con proveedor falso (LSP)."""

import sys
from pathlib import Path

# Agregar raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.agentes.agente_contexto import AgenteContexto
from backend.dominio.interfaces import FuenteUnidadesEconomicas
from backend.servicios.proveedor_falso import ProveedorFalso


class FuenteFalsa(FuenteUnidadesEconomicas):
    """Fuente de datos falsa para pruebas (DIP + LSP)."""

    def cuantificar(self, clave_municipio: str, clase_scian: str) -> int:
        return 3355

    def buscar_area(self, clave_municipio: str, clase_scian: str) -> list[dict]:
        return [
            {"Estrato": "0 a 5 personas", "Sitio_internet": "", "Correo_e": ""},
            {"Estrato": "0 a 5 personas", "Sitio_internet": "", "Correo_e": ""},
            {"Estrato": "6 a 10 personas", "Sitio_internet": "www.ejemplo.com", "Correo_e": "a@b.com"},
        ]


def test_agente_contexto_genera_resumen():
    """El agente debe generar un ResumenZona con datos del DENUE."""
    proveedor = ProveedorFalso(respuestas={
        "Redacta": "En tu municipio hay muchos negocios como el tuyo."
    })
    fuente = FuenteFalsa()
    agente = AgenteContexto(proveedor, fuente)

    resultado = agente.ejecutar({
        "clave_municipio": "14098",
        "clase_scian": "461110",
        "giro_nombre": "Abarrotes",
        "municipio_nombre": "San Pedro Tlaquepaque",
    })

    zona = resultado["resumen_zona"]
    assert zona.total_similares == 3355
    assert zona.con_sitio_web == 1
    assert zona.con_correo == 1
    assert len(zona.texto_resumen) > 0
    assert "0 a 5 personas" in zona.distribucion_tamano
    print("✓ test_agente_contexto_genera_resumen")


def test_agente_contexto_texto_respaldo():
    """Si el modelo devuelve cadena vacía, debe usar texto de respaldo."""
    proveedor = ProveedorFalso(respuestas={"Redacta": ""})
    fuente = FuenteFalsa()
    agente = AgenteContexto(proveedor, fuente)

    resultado = agente.ejecutar({
        "clave_municipio": "14098",
        "clase_scian": "461110",
        "giro_nombre": "Abarrotes",
        "municipio_nombre": "San Pedro Tlaquepaque",
    })

    zona = resultado["resumen_zona"]
    assert "3355" in zona.texto_resumen
    assert "DENUE" in zona.texto_resumen
    print("✓ test_agente_contexto_texto_respaldo")


if __name__ == "__main__":
    test_agente_contexto_genera_resumen()
    test_agente_contexto_texto_respaldo()
    print("\nTodas las pruebas del Agente de contexto pasaron.")

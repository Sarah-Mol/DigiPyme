"""Constantes del dominio: giros, procesos y tablas de impacto.

Cada giro tiene su clase SCIAN y una tabla de impacto por proceso.
Estas tablas las usa el Agente de diagnóstico para calcular prioridades
con código (no con el modelo).
"""

from .entidades import Giro

# ── Seis procesos que evalúa DigiPyme ──────────────────────────────────

PROCESOS = [
    "inventario",
    "ventas_cobro",
    "facturacion_electronica",
    "cobranza_clientes",
    "atencion_presencia_digital",
    "compras_proveedores",
]

NOMBRES_PROCESOS = {
    "inventario": "Inventario",
    "ventas_cobro": "Ventas y cobro",
    "facturacion_electronica": "Facturación electrónica",
    "cobranza_clientes": "Cobranza a clientes",
    "atencion_presencia_digital": "Atención y presencia digital",
    "compras_proveedores": "Compras a proveedores",
}

# ── Catálogo de 6 giros con clase SCIAN ────────────────────────────────

CATALOGO_GIROS: dict[str, Giro] = {
    "abarrotes": Giro(nombre="Abarrotes", clase_scian="461110"),
    "papeleria": Giro(nombre="Papelería", clase_scian="465311"),
    "fonda_restaurante": Giro(nombre="Fonda o restaurante", clase_scian="722511"),
    "taller_mecanico": Giro(nombre="Taller mecánico", clase_scian="811111"),
    "estetica": Giro(nombre="Estética", clase_scian="812110"),
    "ferreteria": Giro(nombre="Ferretería", clase_scian="467111"),
}

# ── Tablas de impacto por giro (1 = bajo, 2 = medio, 3 = alto) ────────
# El impacto indica qué tanto afecta cada proceso al giro.
# Ejemplo: el inventario pesa más en una ferretería que en una estética.

IMPACTO_POR_GIRO: dict[str, dict[str, int]] = {
    "abarrotes": {
        "inventario": 3,
        "ventas_cobro": 3,
        "facturacion_electronica": 2,
        "cobranza_clientes": 1,
        "atencion_presencia_digital": 2,
        "compras_proveedores": 3,
    },
    "papeleria": {
        "inventario": 3,
        "ventas_cobro": 2,
        "facturacion_electronica": 2,
        "cobranza_clientes": 1,
        "atencion_presencia_digital": 2,
        "compras_proveedores": 2,
    },
    "fonda_restaurante": {
        "inventario": 3,
        "ventas_cobro": 3,
        "facturacion_electronica": 2,
        "cobranza_clientes": 1,
        "atencion_presencia_digital": 3,
        "compras_proveedores": 2,
    },
    "taller_mecanico": {
        "inventario": 2,
        "ventas_cobro": 2,
        "facturacion_electronica": 3,
        "cobranza_clientes": 2,
        "atencion_presencia_digital": 2,
        "compras_proveedores": 2,
    },
    "estetica": {
        "inventario": 1,
        "ventas_cobro": 2,
        "facturacion_electronica": 2,
        "cobranza_clientes": 1,
        "atencion_presencia_digital": 3,
        "compras_proveedores": 1,
    },
    "ferreteria": {
        "inventario": 3,
        "ventas_cobro": 2,
        "facturacion_electronica": 2,
        "cobranza_clientes": 2,
        "atencion_presencia_digital": 2,
        "compras_proveedores": 3,
    },
}

# ── Municipio de la demo ───────────────────────────────────────────────

MUNICIPIO_DEMO = "14098"  # San Pedro Tlaquepaque, Jalisco

# ── Rangos de tamaño ───────────────────────────────────────────────────

RANGOS_TAMANO = {
    "micro": "0 a 10 personas",
    "pequena": "11 a 50 personas",
}

/** Tipos compartidos de DigiPyme (TypeScript estricto). */

export interface Ubicacion {
  estado: string;
  municipio: string;
  clave_municipio: string;
}

export interface Evaluacion {
  proceso: string;
  nivel: number; // 0–3
}

export interface PerfilNegocio {
  giro: string;
  tamano: string;
  ubicacion: Ubicacion;
  evaluaciones: Evaluacion[];
}

export interface Recomendacion {
  proceso: string;
  prioridad: number;
  razon: string;
  primer_paso: string;
  fuente: string;
}

export interface ProgramaApoyo {
  id_programa: string;
  nombre: string;
  dependencia: string;
  beneficio: string;
  requisitos: string;
  vigencia: string;
  url: string;
  fecha_verificacion: string;
}

export interface ResumenZona {
  total_similares: number;
  distribucion_tamano: Record<string, number>;
  con_sitio_web: number;
  con_correo: number;
  texto_resumen: string;
}

export interface DiagnosticoResponse {
  reporte_id: string;
  resumen_zona: ResumenZona;
  recomendaciones: Recomendacion[];
  apoyos: ProgramaApoyo[];
  fecha: string;
  aviso: string;
}

export interface GiroOption {
  clave: string;
  nombre: string;
  clase_scian: string;
}

export type Paso = 'inicio' | 'negocio' | 'ubicacion' | 'procesos' | 'progreso' | 'resultados';

/** Nombres legibles de los procesos */
export const NOMBRES_PROCESOS: Record<string, string> = {
  inventario: 'Inventario',
  ventas_cobro: 'Ventas y cobro',
  facturacion_electronica: 'Facturación electrónica',
  cobranza_clientes: 'Cobranza a clientes',
  atencion_presencia_digital: 'Atención y presencia digital',
  compras_proveedores: 'Compras a proveedores',
};

export const OPCIONES_NIVEL: { valor: number; texto: string }[] = [
  { valor: 0, texto: 'No lo llevo' },
  { valor: 1, texto: 'En libreta o papel' },
  { valor: 2, texto: 'En hoja de cálculo o app (sin conectar)' },
  { valor: 3, texto: 'En un sistema integrado' },
];

export const PREGUNTAS_PROCESO: Record<string, string> = {
  inventario: '¿Cómo llevas tu inventario?',
  ventas_cobro: '¿Cómo registras tus ventas y cobros?',
  facturacion_electronica: '¿Cómo haces tus facturas?',
  cobranza_clientes: '¿Cómo llevas la cobranza a clientes?',
  atencion_presencia_digital: '¿Cómo atraes clientes (redes, página, etc.)?',
  compras_proveedores: '¿Cómo haces tus compras a proveedores?',
};

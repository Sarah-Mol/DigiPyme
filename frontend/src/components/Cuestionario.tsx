import { useState, useEffect } from 'react';
import type { Paso, PerfilNegocio, GiroOption } from '../types';
import { NOMBRES_PROCESOS, OPCIONES_NIVEL, PREGUNTAS_PROCESO } from '../types';

interface Props {
  paso: Paso;
  perfil: Partial<PerfilNegocio>;
  onActualizar: (perfil: Partial<PerfilNegocio>) => void;
  onCambiarPaso: (paso: Paso) => void;
  onEnviar: (perfil: PerfilNegocio) => void;
}

const TAMANOS = [
  { valor: 'micro', texto: '1 a 10 personas' },
  { valor: 'pequena', texto: '11 a 50 personas' },
];

// Municipios de la demo (Jalisco)
const MUNICIPIOS = [
  { nombre: 'San Pedro Tlaquepaque', clave: '14098' },
  { nombre: 'Guadalajara', clave: '14039' },
  { nombre: 'Zapopan', clave: '14120' },
  { nombre: 'Tlajomulco de Zúñiga', clave: '14097' },
  { nombre: 'Tonalá', clave: '14101' },
  { nombre: 'El Salto', clave: '14070' },
];

export function Cuestionario({ paso, perfil, onActualizar, onCambiarPaso, onEnviar }: Props) {
  const [giros, setGiros] = useState<GiroOption[]>([]);
  const [evaluaciones, setEvaluaciones] = useState<Record<string, number>>({});

  useEffect(() => {
    fetch('/api/giros')
      .then(r => r.json())
      .then(setGiros)
      .catch(() => {
        // Fallback con datos estáticos
        setGiros([
          { clave: 'abarrotes', nombre: 'Abarrotes', clase_scian: '461110' },
          { clave: 'papeleria', nombre: 'Papelería', clase_scian: '465311' },
          { clave: 'fonda_restaurante', nombre: 'Fonda o restaurante', clase_scian: '722511' },
          { clave: 'taller_mecanico', nombre: 'Taller mecánico', clase_scian: '811111' },
          { clave: 'estetica', nombre: 'Estética', clase_scian: '812110' },
          { clave: 'ferreteria', nombre: 'Ferretería', clase_scian: '467111' },
        ]);
      });
  }, []);

  const progreso = paso === 'negocio' ? 33 : paso === 'ubicacion' ? 66 : 100;
  const procesos = Object.keys(NOMBRES_PROCESOS);

  const todosEvaluados = procesos.every(p => p in evaluaciones);

  const enviar = () => {
    const perfilCompleto: PerfilNegocio = {
      giro: perfil.giro!,
      tamano: perfil.tamano!,
      ubicacion: perfil.ubicacion!,
      evaluaciones: procesos.map(p => ({
        proceso: p,
        nivel: evaluaciones[p] ?? 0,
      })),
    };
    onEnviar(perfilCompleto);
  };

  return (
    <div className="card">
      {/* Barra de avance */}
      <div className="barra-avance">
        <div className="barra-avance-relleno" style={{ width: `${progreso}%` }} />
      </div>

      {/* Pantalla 1: Tu negocio */}
      {paso === 'negocio' && (
        <>
          <h2>Tu negocio</h2>
          <p style={{ marginBottom: '16px', color: '#4a5568' }}>
            ¿A qué se dedica tu negocio?
          </p>
          {giros.map(g => (
            <button
              key={g.clave}
              className={`opcion ${perfil.giro === g.clave ? 'seleccionada' : ''}`}
              onClick={() => onActualizar({ ...perfil, giro: g.clave })}
            >
              {g.nombre}
            </button>
          ))}

          {perfil.giro && (
            <>
              <p style={{ marginTop: '16px', marginBottom: '8px', color: '#4a5568' }}>
                ¿Cuántas personas trabajan en tu negocio?
              </p>
              {TAMANOS.map(t => (
                <button
                  key={t.valor}
                  className={`opcion ${perfil.tamano === t.valor ? 'seleccionada' : ''}`}
                  onClick={() => onActualizar({ ...perfil, tamano: t.valor })}
                >
                  {t.texto}
                </button>
              ))}
            </>
          )}

          {perfil.giro && perfil.tamano && (
            <button
              className="btn"
              style={{ marginTop: '16px' }}
              onClick={() => onCambiarPaso('ubicacion')}
            >
              Siguiente →
            </button>
          )}
        </>
      )}

      {/* Pantalla 2: Dónde estás */}
      {paso === 'ubicacion' && (
        <>
          <h2>Dónde estás</h2>
          <p style={{ marginBottom: '16px', color: '#4a5568' }}>
            ¿En qué municipio está tu negocio?
          </p>
          {MUNICIPIOS.map(m => (
            <button
              key={m.clave}
              className={`opcion ${perfil.ubicacion?.clave_municipio === m.clave ? 'seleccionada' : ''}`}
              onClick={() => onActualizar({
                ...perfil,
                ubicacion: {
                  estado: 'Jalisco',
                  municipio: m.nombre,
                  clave_municipio: m.clave,
                },
              })}
            >
              {m.nombre}, Jalisco
            </button>
          ))}

          <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
            <button
              className="btn"
              style={{ background: '#718096' }}
              onClick={() => onCambiarPaso('negocio')}
            >
              ← Atrás
            </button>
            <button
              className="btn"
              disabled={!perfil.ubicacion}
              onClick={() => onCambiarPaso('procesos')}
            >
              Siguiente →
            </button>
          </div>
        </>
      )}

      {/* Pantalla 3: Cómo operas hoy */}
      {paso === 'procesos' && (
        <>
          <h2>Cómo operas hoy</h2>
          {procesos.map(p => (
            <div key={p} style={{ marginBottom: '20px' }}>
              <p style={{ fontWeight: 600, marginBottom: '8px' }}>
                {PREGUNTAS_PROCESO[p]}
              </p>
              {OPCIONES_NIVEL.map(op => (
                <button
                  key={op.valor}
                  className={`opcion ${evaluaciones[p] === op.valor ? 'seleccionada' : ''}`}
                  onClick={() => setEvaluaciones({ ...evaluaciones, [p]: op.valor })}
                >
                  {op.texto}
                </button>
              ))}
              <button
                className={`opcion ${evaluaciones[p] === -1 ? 'seleccionada' : ''}`}
                style={{ fontStyle: 'italic', color: '#718096' }}
                onClick={() => setEvaluaciones({ ...evaluaciones, [p]: 0 })}
              >
                No sé
              </button>
            </div>
          ))}

          <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
            <button
              className="btn"
              style={{ background: '#718096' }}
              onClick={() => onCambiarPaso('ubicacion')}
            >
              ← Atrás
            </button>
            <button
              className="btn btn-secondary"
              disabled={!todosEvaluados}
              onClick={enviar}
            >
              Obtener diagnóstico
            </button>
          </div>
        </>
      )}
    </div>
  );
}

import { useState } from 'react';
import type { Paso, PerfilNegocio, DiagnosticoResponse } from './types';
import { Inicio } from './components/Inicio';
import { Cuestionario } from './components/Cuestionario';
import { Progreso } from './components/Progreso';
import { Resultados } from './components/Resultados';

/** Estilos globales en línea (funciona en celular desde 360px). */
const estilosGlobales = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: #f0f4f8;
    color: #1a202c;
    line-height: 1.6;
  }
  .app {
    max-width: 600px;
    margin: 0 auto;
    padding: 16px;
    min-height: 100vh;
  }
  .card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }
  .btn {
    display: inline-block;
    background: #2b6cb0;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 1rem;
    cursor: pointer;
    width: 100%;
    text-align: center;
    transition: background 0.2s;
  }
  .btn:hover { background: #2c5282; }
  .btn:disabled { background: #a0aec0; cursor: not-allowed; }
  .btn-secondary {
    background: #38a169;
  }
  .btn-secondary:hover { background: #2f855a; }
  h1 { font-size: 1.5rem; color: #1a365d; margin-bottom: 8px; }
  h2 { font-size: 1.25rem; color: #2d3748; margin-bottom: 12px; }
  .barra-avance {
    height: 6px;
    background: #e2e8f0;
    border-radius: 3px;
    margin-bottom: 20px;
    overflow: hidden;
  }
  .barra-avance-relleno {
    height: 100%;
    background: #2b6cb0;
    border-radius: 3px;
    transition: width 0.3s ease;
  }
  .opcion {
    display: block;
    width: 100%;
    text-align: left;
    background: #f7fafc;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    cursor: pointer;
    font-size: 0.95rem;
    transition: all 0.2s;
  }
  .opcion:hover { border-color: #2b6cb0; background: #ebf8ff; }
  .opcion.seleccionada { border-color: #2b6cb0; background: #ebf8ff; font-weight: 600; }
  .semaforo {
    display: inline-block;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    margin-right: 8px;
    vertical-align: middle;
  }
  .rojo { background: #e53e3e; }
  .amarillo { background: #ecc94b; }
  .verde { background: #38a169; }
  .aviso {
    background: #fffff0;
    border: 1px solid #ecc94b;
    border-radius: 8px;
    padding: 12px;
    font-size: 0.9rem;
    font-style: italic;
    margin: 16px 0;
  }
  .apoyo-card {
    background: #f0fff4;
    border-left: 4px solid #38a169;
    padding: 12px 16px;
    margin-bottom: 12px;
    border-radius: 0 8px 8px 0;
  }
  .rec-card {
    background: #ebf8ff;
    border-left: 4px solid #2b6cb0;
    padding: 12px 16px;
    margin-bottom: 12px;
    border-radius: 0 8px 8px 0;
  }
  .fuente { font-size: 0.8rem; color: #718096; }
  a { color: #2b6cb0; }
  .progreso-msg {
    text-align: center;
    padding: 40px 20px;
  }
  .spinner {
    width: 40px; height: 40px;
    border: 4px solid #e2e8f0;
    border-top-color: #2b6cb0;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
`;

export function App() {
  const [paso, setPaso] = useState<Paso>('inicio');
  const [perfil, setPerfil] = useState<Partial<PerfilNegocio>>({});
  const [resultado, setResultado] = useState<DiagnosticoResponse | null>(null);
  const [error, setError] = useState<string>('');

  const enviarDiagnostico = async (perfilCompleto: PerfilNegocio) => {
    setPaso('progreso');
    setError('');
    try {
      const resp = await fetch('/api/diagnostico', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(perfilCompleto),
      });
      if (!resp.ok) {
        const data = await resp.json();
        throw new Error(data.detail || 'Error al generar el diagnóstico');
      }
      const data: DiagnosticoResponse = await resp.json();
      setResultado(data);
      setPaso('resultados');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error de conexión');
      setPaso('inicio');
    }
  };

  const reiniciar = () => {
    setPaso('inicio');
    setPerfil({});
    setResultado(null);
    setError('');
  };

  return (
    <>
      <style>{estilosGlobales}</style>
      <div className="app">
        {paso === 'inicio' && (
          <Inicio
            error={error}
            onEmpezar={() => setPaso('negocio')}
          />
        )}

        {(paso === 'negocio' || paso === 'ubicacion' || paso === 'procesos') && (
          <Cuestionario
            paso={paso}
            perfil={perfil}
            onActualizar={setPerfil}
            onCambiarPaso={setPaso}
            onEnviar={enviarDiagnostico}
          />
        )}

        {paso === 'progreso' && <Progreso />}

        {paso === 'resultados' && resultado && (
          <Resultados
            resultado={resultado}
            onReiniciar={reiniciar}
          />
        )}
      </div>
    </>
  );
}

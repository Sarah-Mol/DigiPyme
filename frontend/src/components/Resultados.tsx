import type { DiagnosticoResponse } from '../types';

interface Props {
  resultado: DiagnosticoResponse;
  onReiniciar: () => void;
}

function colorSemaforo(prioridad: number): string {
  if (prioridad >= 6) return 'rojo';
  if (prioridad >= 3) return 'amarillo';
  return 'verde';
}

export function Resultados({ resultado, onReiniciar }: Props) {
  const { resumen_zona, recomendaciones, apoyos, fecha, aviso, reporte_id } = resultado;

  return (
    <>
      {/* Resumen de zona */}
      <div className="card">
        <h2>📍 Tu zona</h2>
        <p>{resumen_zona.texto_resumen}</p>
        <p style={{ marginTop: '8px' }}>
          <strong>{resumen_zona.total_similares}</strong> negocios similares
          en tu municipio
        </p>
      </div>

      {/* Procesos priorizados */}
      <div className="card">
        <h2>📊 Procesos a digitalizar</h2>
        <p style={{ color: '#4a5568', marginBottom: '16px' }}>
          Ordenados de mayor a menor prioridad. Los 3 primeros son tus prioridades.
        </p>
        {recomendaciones.map((rec, i) => (
          <div key={rec.proceso} className="rec-card">
            <div>
              <span className={`semaforo ${colorSemaforo(rec.prioridad)}`} />
              <strong>{rec.proceso}</strong>
              {i < 3 && ' ⭐'}
              <span style={{ float: 'right', color: '#718096', fontSize: '0.85rem' }}>
                Prioridad: {rec.prioridad}
              </span>
            </div>
            <p style={{ marginTop: '8px' }}>
              <em>¿Por qué?</em> {rec.razon}
            </p>
            <p>
              <em>Primer paso:</em> {rec.primer_paso}
            </p>
            <p className="fuente">{rec.fuente}</p>
          </div>
        ))}
      </div>

      {/* Apoyos */}
      <div className="card">
        <h2>🏛️ Apoyos y programas públicos</h2>
        {apoyos.length === 0 ? (
          <p>
            No se encontraron programas que apliquen a tu perfil en este momento.
            Consulta la oficina de desarrollo económico de tu municipio.
          </p>
        ) : (
          apoyos.map(apoyo => (
            <div key={apoyo.id_programa} className="apoyo-card">
              <strong>{apoyo.nombre}</strong>
              <span style={{ color: '#718096' }}> ({apoyo.dependencia})</span>
              <p style={{ marginTop: '4px' }}>
                <em>Qué ofrece:</em> {apoyo.beneficio}
              </p>
              <p><em>Requisitos:</em> {apoyo.requisitos}</p>
              <p><em>Vigencia:</em> {apoyo.vigencia}</p>
              <p>
                <a href={apoyo.url} target="_blank" rel="noopener noreferrer">
                  Ver fuente oficial ↗
                </a>
                <span className="fuente"> | Verificado: {apoyo.fecha_verificacion}</span>
              </p>
            </div>
          ))
        )}
      </div>

      {/* Aviso y descarga */}
      <div className="card">
        <div className="aviso">{aviso}</div>
        <p className="fuente" style={{ marginBottom: '16px' }}>
          Diagnóstico generado el {fecha}
        </p>
        <a
          href={`/api/reporte/${reporte_id}`}
          download
          className="btn btn-secondary"
          style={{ display: 'block', textDecoration: 'none' }}
        >
          📄 Descargar mi reporte
        </a>
        <button
          className="btn"
          style={{ marginTop: '8px' }}
          onClick={onReiniciar}
        >
          Hacer otro diagnóstico
        </button>
        <p style={{ textAlign: 'center', marginTop: '16px' }} className="fuente">
          DigiPyme · ODS 9 · Hackathon SoftwareChido 2026B · ITESO
        </p>
      </div>
    </>
  );
}

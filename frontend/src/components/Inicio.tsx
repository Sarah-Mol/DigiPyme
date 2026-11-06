interface Props {
  error: string;
  onEmpezar: () => void;
}

export function Inicio({ error, onEmpezar }: Props) {
  return (
    <div className="card" style={{ textAlign: 'center', paddingTop: '40px' }}>
      <h1>🏪 DigiPyme</h1>
      <p style={{ fontSize: '1.1rem', color: '#4a5568', marginBottom: '8px' }}>
        Diagnóstico de digitalización para tu negocio
      </p>
      <p style={{ fontSize: '0.9rem', color: '#718096', marginBottom: '24px' }}>
        Responde unas preguntas sobre tu negocio y recibe un diagnóstico
        con recomendaciones y apoyos públicos disponibles.
        <br />Tarda menos de 10 minutos. No necesitas cuenta.
      </p>

      {error && (
        <div style={{
          background: '#fff5f5', border: '1px solid #fc8181',
          borderRadius: '8px', padding: '12px', marginBottom: '16px',
          color: '#c53030', fontSize: '0.9rem',
        }}>
          {error}
        </div>
      )}

      <button className="btn" onClick={onEmpezar}>
        Empezar diagnóstico
      </button>

      <p style={{ fontSize: '0.75rem', color: '#a0aec0', marginTop: '24px' }}>
        ODS 9: Industria, innovación e infraestructura
        <br />Hackathon Agéntico SoftwareChido 2026B · ITESO
      </p>
    </div>
  );
}

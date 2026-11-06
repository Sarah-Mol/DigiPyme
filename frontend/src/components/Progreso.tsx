import { useState, useEffect } from 'react';

const MENSAJES = [
  'Buscando negocios como el tuyo...',
  'Analizando tus procesos...',
  'Buscando apoyos disponibles...',
  'Preparando tu diagnóstico...',
];

export function Progreso() {
  const [indice, setIndice] = useState(0);

  useEffect(() => {
    const intervalo = setInterval(() => {
      setIndice(i => (i < MENSAJES.length - 1 ? i + 1 : i));
    }, 4000);
    return () => clearInterval(intervalo);
  }, []);

  return (
    <div className="card progreso-msg">
      <div className="spinner" />
      <h2>Generando tu diagnóstico</h2>
      <p style={{ color: '#4a5568', marginTop: '12px' }}>
        {MENSAJES[indice]}
      </p>
      <p style={{ fontSize: '0.85rem', color: '#a0aec0', marginTop: '24px' }}>
        Esto puede tardar hasta 90 segundos.
        <br />Estamos analizando tu negocio con datos del DENUE del INEGI.
      </p>
    </div>
  );
}

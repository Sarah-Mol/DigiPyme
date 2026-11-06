"""Constructor de reporte (patrón Builder).

Arma el reporte PDF paso a paso: portada, resumen, zona, procesos,
apoyos y fuentes. No es un agente porque no necesita razonar;
solo arma el documento (sección 5.5 del documento de visión).
"""

from __future__ import annotations

from datetime import datetime

from backend.dominio.entidades import Diagnostico, Reporte


class ConstructorReporte:
    """Builder: construye el reporte HTML que se convierte a PDF.

    SRP: su única responsabilidad es armar el documento.
    """

    def __init__(self, diagnostico: Diagnostico) -> None:
        self._diagnostico = diagnostico
        self._secciones: list[str] = []
        self._css = self._generar_css()

    def _generar_css(self) -> str:
        return """
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px;
                   color: #333; line-height: 1.6; max-width: 800px; }
            h1 { color: #1a5276; border-bottom: 3px solid #2ecc71; padding-bottom: 10px; }
            h2 { color: #2c3e50; margin-top: 30px; }
            .semaforo { display: inline-block; width: 16px; height: 16px;
                        border-radius: 50%; margin-right: 8px; vertical-align: middle; }
            .rojo { background: #e74c3c; }
            .amarillo { background: #f39c12; }
            .verde { background: #2ecc71; }
            .prioridad { background: #f8f9fa; border-left: 4px solid #3498db;
                         padding: 15px; margin: 10px 0; border-radius: 4px; }
            .apoyo { background: #eaf7e6; border-left: 4px solid #27ae60;
                     padding: 15px; margin: 10px 0; border-radius: 4px; }
            .aviso { background: #fff3cd; border: 1px solid #ffc107;
                     padding: 15px; margin: 20px 0; border-radius: 4px;
                     font-style: italic; }
            .fuente { font-size: 0.85em; color: #7f8c8d; }
            table { border-collapse: collapse; width: 100%; margin: 15px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background: #2c3e50; color: white; }
        </style>
        """

    def con_portada(self) -> ConstructorReporte:
        """Agrega la portada con datos del negocio."""
        d = self._diagnostico
        self._secciones.append(f"""
        <h1>DigiPyme – Diagnóstico de Digitalización</h1>
        <table>
            <tr><th>Giro</th><td>{d.perfil.giro.nombre}</td></tr>
            <tr><th>Tamaño</th><td>{d.perfil.tamano}</td></tr>
            <tr><th>Municipio</th><td>{d.perfil.ubicacion.municipio},
                {d.perfil.ubicacion.estado}</td></tr>
            <tr><th>Fecha</th><td>{d.fecha or datetime.now().strftime('%d/%m/%Y')}</td></tr>
        </table>
        """)
        return self

    def con_resumen(self) -> ConstructorReporte:
        """Agrega el resumen ejecutivo."""
        total_rec = len(self._diagnostico.recomendaciones)
        top = self._diagnostico.recomendaciones[:3] if self._diagnostico.recomendaciones else []
        top_nombres = ", ".join(r.proceso for r in top)
        self._secciones.append(f"""
        <h2>Resumen</h2>
        <p>Se evaluaron {total_rec} procesos de tu negocio.
        Las prioridades principales son: <strong>{top_nombres}</strong>.</p>
        """)
        return self

    def con_zona(self) -> ConstructorReporte:
        """Agrega el resumen de la zona."""
        zona = self._diagnostico.resumen_zona
        self._secciones.append(f"""
        <h2>Tu zona</h2>
        <p>{zona.texto_resumen}</p>
        <p>Negocios similares en tu municipio: <strong>{zona.total_similares}</strong></p>
        """)
        return self

    def con_procesos(self) -> ConstructorReporte:
        """Agrega los procesos priorizados con semáforo."""
        self._secciones.append("<h2>Procesos a digitalizar</h2>")
        for i, rec in enumerate(self._diagnostico.recomendaciones):
            # Semáforo: rojo si prioridad >= 6, amarillo >= 3, verde < 3
            if rec.prioridad >= 6:
                color = "rojo"
            elif rec.prioridad >= 3:
                color = "amarillo"
            else:
                color = "verde"

            destacado = " ⭐" if i < 3 else ""
            self._secciones.append(f"""
            <div class="prioridad">
                <span class="semaforo {color}"></span>
                <strong>{rec.proceso}{destacado}</strong>
                (prioridad: {rec.prioridad})
                <br><em>¿Por qué?</em> {rec.razon}
                <br><em>Primer paso:</em> {rec.primer_paso}
                <br><span class="fuente">{rec.fuente}</span>
            </div>
            """)
        return self

    def con_apoyos(self) -> ConstructorReporte:
        """Agrega los apoyos recomendados."""
        self._secciones.append("<h2>Apoyos y programas públicos</h2>")
        if not self._diagnostico.apoyos:
            self._secciones.append(
                "<p>No se encontraron programas que apliquen a tu perfil en "
                "este momento. Consulta la oficina de desarrollo económico "
                "de tu municipio.</p>"
            )
        else:
            for apoyo in self._diagnostico.apoyos:
                self._secciones.append(f"""
                <div class="apoyo">
                    <strong>{apoyo.nombre}</strong> ({apoyo.dependencia})
                    <br><em>Qué ofrece:</em> {apoyo.beneficio}
                    <br><em>Requisitos:</em> {apoyo.requisitos}
                    <br><em>Vigencia:</em> {apoyo.vigencia}
                    <br><a href="{apoyo.url}" target="_blank">Ver fuente oficial</a>
                    <span class="fuente"> | Verificado: {apoyo.fecha_verificacion}</span>
                </div>
                """)
        return self

    def con_fuentes(self) -> ConstructorReporte:
        """Agrega las fuentes y el aviso legal."""
        self._secciones.append(f"""
        <div class="aviso">{self._diagnostico.aviso}</div>
        <h2>Fuentes</h2>
        <ul>
            <li>INEGI, API del DENUE
                (<a href="https://www.inegi.org.mx/servicios/api_denue.html">enlace</a>)</li>
            <li>Catálogo de apoyos verificado por el equipo DigiPyme</li>
        </ul>
        <p class="fuente">Generado por DigiPyme – Hackathon Agéntico SoftwareChido 2026B
        – ODS 9: Industria, innovación e infraestructura</p>
        """)
        return self

    def construir(self) -> Reporte:
        """Construye el reporte final."""
        html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Reporte DigiPyme</title>{self._css}</head>
<body>
{''.join(self._secciones)}
</body>
</html>"""
        return Reporte(diagnostico=self._diagnostico, contenido_html=html)

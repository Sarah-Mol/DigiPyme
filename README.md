# DigiPyme – Diagnóstico de digitalización para MiPyMEs

Plataforma web que evalúa el nivel de digitalización de micro y pequeñas empresas
y genera recomendaciones priorizadas con programas de apoyo gubernamental vigentes.

**ODS 9** – Industria, innovación e infraestructura (metas 9.3 y 9.5).

## Arquitectura

4 capas: interfaz web → API REST → orquestación con agentes → servicios externos.

| Capa | Tecnología |
|------|-----------|
| Frontend | React 18 + TypeScript + Vite |
| API | Python + FastAPI |
| Agentes | Clases Python (Template Method, Strategy, Façade) |
| Externos | DENUE API · Catálogo JSON · Ollama (local) |

### Patrones de diseño

- **Strategy** → `ProveedorModelo` (Ollama / Falso para tests)
- **Adapter** → `AdaptadorDENUE` (normaliza respuestas del INEGI)
- **Proxy cache** → `ProxyCacheDENUE` (evita llamadas repetidas)
- **Façade** → `Orquestador.diagnosticar()` (coordina los 3 agentes)
- **Template Method** → `Agente.ejecutar()` → `recolectar → razonar → validar`
- **Builder** → `ConstructorReporte` (genera HTML del reporte)

### Principios SOLID

- **SRP**: cada agente tiene una sola responsabilidad
- **OCP**: el cache se agrega sin modificar el adaptador
- **DIP**: los agentes dependen de interfaces, no de implementaciones
- **LSP**: `ProveedorFalso` sustituye a `ProveedorOllama` en pruebas

## Requisitos

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com/) con modelo `qwen2.5:7b`
- Token de la [API DENUE](https://www.inegi.org.mx/app/api/denue/v1/tokenVerify.aspx)

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/DigiPyme.git
cd DigiPyme

# 2. Backend
cp .env.example .env
# Editar .env con tu token DENUE
pip install -r backend/requirements.txt

# 3. Frontend
cd frontend
npm install
cd ..

# 4. Descargar modelo de Ollama
ollama pull qwen2.5:7b
```

## Ejecución

```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: Backend (puerto 8000)
uvicorn backend.main:app --reload

# Terminal 3: Frontend (puerto 5173)
cd frontend && npm run dev
```

Abrir http://localhost:5173

## Pruebas

```bash
# Todas las pruebas (no requieren Ollama ni DENUE)
python -m tests.test_agente_contexto
python -m tests.test_agente_diagnostico
python -m tests.test_agente_apoyos
python -m tests.test_orquestador
```

Las pruebas usan `ProveedorFalso` (LSP) y fuentes/catálogos falsos (DIP),
por lo que no necesitan conexión a internet ni servicios externos.

## Estructura del proyecto

```
DigiPyme/
├── backend/
│   ├── main.py                 # Punto de entrada FastAPI
│   ├── config.py               # Configuración (.env)
│   ├── orquestador.py          # Façade: coordina agentes
│   ├── agentes/
│   │   ├── agente_base.py      # Template Method abstracto
│   │   ├── agente_contexto.py  # CU-2: Consulta DENUE
│   │   ├── agente_diagnostico.py # CU-3: Prioriza procesos
│   │   └── agente_apoyos.py    # CU-4: Filtra programas
│   ├── dominio/
│   │   ├── entidades.py        # Dataclasses del dominio
│   │   ├── interfaces.py       # ABCs (DIP)
│   │   └── constantes.py       # Giros, procesos, impactos
│   ├── servicios/
│   │   ├── proveedor_ollama.py # Strategy: Ollama
│   │   ├── proveedor_falso.py  # Strategy: pruebas (LSP)
│   │   ├── adaptador_denue.py  # Adapter + Proxy cache
│   │   ├── catalogo_apoyos_json.py # Catálogo cerrado
│   │   └── constructor_reporte.py  # Builder: HTML
│   ├── api/
│   │   └── rutas.py            # Endpoints REST
│   └── datos/
│       └── catalogo_apoyos.json # 8 programas verificados
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Flujo principal
│   │   ├── types/index.ts      # Interfaces TypeScript
│   │   └── components/
│   │       ├── Inicio.tsx
│   │       ├── Cuestionario.tsx # 3 pantallas
│   │       ├── Progreso.tsx
│   │       └── Resultados.tsx
│   ├── package.json
│   └── vite.config.ts
├── tests/
│   ├── test_agente_contexto.py
│   ├── test_agente_diagnostico.py
│   ├── test_agente_apoyos.py
│   └── test_orquestador.py
├── docs/
│   ├── casos_de_uso.puml
│   ├── componentes.puml
│   ├── clases.puml
│   └── secuencias.puml
└── .env.example
```

## Giros soportados

| Giro | SCIAN |
|------|-------|
| Abarrotes | 461110 |
| Papelería | 465311 |
| Fonda / Restaurante | 722511 |
| Taller mecánico | 811111 |
| Estética | 812110 |
| Ferretería | 467111 |

## Fórmula de prioridad

```
prioridad = (3 − nivel_actual) × impacto_del_proceso_para_el_giro
```

Donde `nivel_actual` es 0–3 y `impacto` es 1–3 según tabla por giro.

## Equipo

- **Sarah Moreno** – Arquitectura, agentes y backend
- **Jimena Corona** – Frontend y UX
- **Emiliano del Toro** – DENUE, programas de apoyo, pruebas y video

## Metodología

**AI-DLC**: la IA propone; el equipo decide, valida y prueba.

## Licencia

Proyecto académico – Hackathon Agéntico SoftwareChido 2026B – ITESO.

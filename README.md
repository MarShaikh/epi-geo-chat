# Epi-Geo Chat: AI-Powered Geospatial Data Query System

A multi-agent chat interface for querying and analysing geospatial climate data stored in Azure GeoCatalog.

---

## Overview

Ask natural language questions about climate data and get intelligent responses, visualisations, and automated analysis:

- *"Show me rainfall in Lagos for February 2024"*
- *"What collections do we have?"*
- *"Show me a precipitation trend chart for Kano in 2023"*

The system uses a **5-agent pipeline** with intent-based routing to parse queries, resolve locations, search STAC catalogs, generate analysis code, and synthesise responses.

### Demos

#### Chat Demo
<video src="https://github.com/user-attachments/assets/78e5354e-7d6d-422c-8c83-0c7170580d2d" controls width="100%"></video>

#### Map Exploration
<video src="https://github.com/user-attachments/assets/736220b0-0b13-4803-9fb6-dc20dd7d08ec" controls width="100%"></video>

---

## Architecture

### Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12 + FastAPI (async) |
| **LLM / Agents** | Azure OpenAI GPT-4o via Microsoft Agent Framework |
| **STAC Catalog** | Azure GeoCatalog (STAC API + TiTiler) |
| **Vector Store** | ChromaDB (Azure Container Apps + Azure File Share) |
| **Code Execution** | Docker sandbox (`epi-geo-sandbox:latest`) |
| **Frontend** | React 18 + TypeScript + Vite + Tailwind CSS v4 + Leaflet |
| **Observability** | OpenTelemetry + Azure Monitor |

### Agent Pipeline

```
User Query -> Parser -> RAG Collection Resolver -> Geocoder -> STAC Search -> [Code Gen + Sandbox] -> Synthesiser -> Response
```

Each agent uses Pydantic structured outputs for type-safe handoffs. The code generation step only runs for `analysis` intent queries. See [docs/agent_architecture.md](docs/agent_architecture.md) for full details.

### Key Components

- **RAG Collection Resolution** — ChromaDB semantic search maps user keywords to STAC collection IDs. See [docs/rag.md](docs/rag.md).
- **Observability** — Per-agent tracing with `@traced_agent` decorators and Azure Monitor. See [docs/observability.md](docs/observability.md).
- **Evaluations** — Golden dataset with accuracy, precision, recall, and bbox IoU metrics. See [docs/evaluations.md](docs/evaluations.md).

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker
- Azure CLI (authenticated)

### Local Development (Docker Compose)

```bash
# Clone and configure
git clone <repo-url> && cd epi-geo-chat
cp .env.example .env
# Edit .env with your credentials (see Environment Variables below)

# Build sandbox image
docker build -t epi-geo-sandbox:latest src/code_executor/docker/

# Start all services
docker compose up --build
```

Backend runs on `http://localhost:8000`, frontend on `http://localhost:5173`.

### Manual Setup

```bash
# Backend
conda create -n epi-geo-chat python=3.12 -y && conda activate epi-geo-chat
pip install -r requirements/base.txt
uvicorn src.api.app:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Index ChromaDB (once, or when collections change)
python scripts/index_collections.py
```

### Environment Variables

```env
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=preview
GEOCATALOG_URL=
GEOCATALOG_SCOPE=
AZURE_MAPS_SUBSCRIPTION_KEY=
CHROMA_CLIENT_URL=
APPLICATIONINSIGHTS_CONNECTION_STRING=   # optional
```

---

## Project Structure

```
epi-geo-chat/
├── src/
│   ├── agents/                    # 5-agent pipeline
│   │   ├── workflow.py            # AgentWorkflow orchestrator
│   │   ├── agent_runners.py       # Typed async wrappers with tracing
│   │   ├── agent_config.py        # Azure OpenAI client factory
│   │   ├── query_parser.py        # Agent 1: intent + extraction
│   │   ├── geocoding_temporal.py  # Agent 2: bbox + datetime
│   │   ├── stac_coordinator.py    # Agent 3: STAC search
│   │   ├── code_generator.py      # Agent 4: analysis code gen
│   │   └── response_synthesizer.py # Agent 5: final response
│   ├── api/                       # FastAPI backend
│   │   ├── app.py
│   │   ├── schemas.py
│   │   └── routes/                # chat, stac, tiles, artifacts, health
│   ├── code_executor/             # Sandboxed code execution
│   │   ├── validator.py           # AST security validation
│   │   ├── sandbox.py             # Docker sandbox
│   │   ├── artifact_store.py      # File store with 60-min TTL
│   │   └── docker/Dockerfile
│   ├── rag/                       # ChromaDB vector store + resolvers
│   └── stac/                      # GeoCatalog client + geocoding
│       └── data/                  # Lookup data (state bboxes)
├── frontend/src/                  # React + TypeScript + Leaflet
│   ├── components/
│   │   ├── chat/                  # Chat panel + agent progress
│   │   ├── map/                   # Map + draw control + tile overlay
│   │   ├── results/               # STAC results display
│   │   ├── explorer/              # STAC Explorer (direct browsing)
│   │   └── analysis/              # Code + artifacts display
│   ├── context/                   # Global state (useReducer)
│   └── hooks/                     # useChat, useMap, useExplorer
├── data/                          # Generated data (STAC inventory)
├── infra/                         # Infrastructure configs
├── tests/                         # Unit tests + evaluation framework
├── scripts/                       # Index collections, test scripts
├── docs/                          # Architecture, RAG, observability docs
└── docker-compose.yml             # Local dev orchestration
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/health/ready` | Readiness (validates ChromaDB) |
| POST | `/api/v1/chat` | Synchronous chat |
| GET | `/api/v1/chat/stream` | SSE streaming chat |
| GET | `/api/v1/stac/collections` | List STAC collections |
| POST | `/api/v1/stac/search` | Search items (bbox, datetime, collections) |
| GET | `/api/v1/tiles/{collection}/{item}/crop/{bbox}.png` | Tile proxy |
| GET | `/api/v1/artifacts/{artifact_id}` | Serve analysis output files |

---

## Documentation

| Document | Description |
|---|---|
| [agent_architecture.md](docs/agent_architecture.md) | Full pipeline flow, agent details, mermaid diagram |
| [rag.md](docs/rag.md) | ChromaDB setup, collection resolution, infrastructure |
| [observability.md](docs/observability.md) | OpenTelemetry tracing setup |
| [evaluations.md](docs/evaluations.md) | Evaluation framework and metrics |
| [agent_framework.md](docs/agent_framework.md) | Framework choice rationale |
| [local-development.md](docs/local-development.md) | Docker Compose setup and troubleshooting |

---

## Contact

**Marouf Shaikh**
GitHub: MarShaikh

Inspired by [Microsoft Earth Copilot](https://github.com/microsoft/Earth-Copilot) (simplified from 13 to 5 agents).

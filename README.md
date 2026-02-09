# Epi-Geo Chat: AI-Powered Geospatial Data Query System

A multi-agent chat interface for querying geospatial climate data.

---

## Overview

Ask natural language questions about climate data and get intelligent responses:

- *"Show me rainfall in Lagos for February 2024"*
- *"What's the temperature trend in Kano last month?"*
- *"Get me vegetation data for Nigeria in 2023"*

The system uses a 4-agent pipeline to:
1. Parse natural language queries
2. Resolve locations and dates
3. Search the Azure GeoCatalog STAC API
4. Generate natural language summaries

---

## Architecture

### Tech Stack

**AI Framework:**
- Microsoft Agent Framework (Preview)
- Azure OpenAI GPT-4o (Sweden Central)
- Pydantic for structured outputs

**Data Layer:**
- Azure GeoCatalog (STAC API)
- Azure Maps (Geocoding)
- Azure Blob Storage (COG assets)
- ChromaDB for RAG-based collection resolution

**Observability:**
- Azure Monitor (Application Insights)
- OpenTelemetry tracing with custom decorators
- Per-agent span capture with argument/output serialization

**Evaluations:**
- Custom evaluation framework with golden dataset
- Accuracy, Precision, Recall, and IoU metrics

**Future Components:**
- FastAPI backend
- React + TypeScript frontend
- Docker for code execution

### Agent Pipeline

```
User Query → Parser → Collection Resolver (RAG) → Geocoder → STAC Search → Synthesizer → Response
```

**Agent 1: Query Parser**
- Extracts intent, collections, location, and temporal references
- Returns: `ParsedQuery` (Pydantic model)

**Agent 2: Geocoding & Temporal Resolver**
- Converts locations to bounding boxes using 3-tier fallback:
  1. Local lookup (predefined regions)
  2. Azure Maps API
  3. LLM fallback
- Converts relative dates ("last month") to ISO 8601
- Returns: `GeocodingResult` with bbox and datetime

**Agent 3: STAC Query Coordinator**
- Searches Azure GeoCatalog STAC API
- Uses `search_and_summarize()` function to process results
- Returns: `STACSearchResult` with count, date range, and sample items

**Agent 4: Response Synthesizer**
- Generates natural language response from search results
- Returns: User-friendly summary

### RAG: Collection Resolution

The system uses **ChromaDB** for semantic collection resolution. User keywords (e.g., "rainfall", "temperature") are matched against indexed STAC collection metadata to find the most relevant collection IDs, avoiding hardcoded mappings.

- `CollectionVectorStore` (`src/rag/vector_store.py`) — Indexes collection titles, descriptions, and keywords into ChromaDB; performs semantic search
- `resolve_collections_by_keywords()` (`src/rag/collection_resolver.py`) — Convenience function used in the agent workflow
- `scripts/index_collections.py` — Populates the vector store from the GeoCatalog API

See [docs/rag.md](docs/rag.md) for details.

### Observability

End-to-end tracing with **Azure Monitor OpenTelemetry**. Each agent is decorated with `@traced_agent` to capture inputs/outputs as span attributes, with workflow-level trace ID correlation in Application Insights.

See [docs/observability.md](docs/observability.md) for details.

### Evaluations

Custom evaluation framework with a golden dataset of 8 annotated queries. Computes accuracy, precision, recall per field, and bounding box IoU.

```bash
python tests/evaluation/evaluate.py
```

See [docs/evaluations.md](docs/evaluations.md) for details.

---

## Setup

### Prerequisites

- Python 3.11+
- Azure subscription
- Azure CLI

### 1. Azure Infrastructure

#### Azure OpenAI (Sweden Central)

```bash
# Create resource
az cognitiveservices account create \
  --name <name> \
  --resource-group <resource-group-name> \
  --location swedencentral \
  --kind OpenAI \
  --sku s0 \
  --custom-domain <custom-domain-name>

# Get endpoint
az cognitiveservices account show \
  --name  \
  --resource-group <resource-group-name> \
  | jq -r .properties.endpoint

# Get API key
az cognitiveservices account keys list \
  --name <name> \
  --resource-group <resource-group-name> \
  | jq -r .key1

# Deploy GPT-4o
az cognitiveservices account deployment create \
  --name <name> \
  --resource-group <resource-group-name> \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version "2024-11-20" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "GlobalStandard"
```

#### Azure Maps

```bash
# Create Maps account
az maps account create \
  -n <name> \
  -g <resource-group-name> \
  --sku G2 \
  --kind "Gen2"

# Get key
az maps account keys list -n <name> -g <resource-group-name>
```

#### (Optional) Key Vault

```bash
# Create Key Vault
az keyvault create -n <keyvault-name> -g <resource-group-name> -l westeurope

# Store Maps key
AZURE_MAPS_KEY=$(az maps account keys list -n <name> --query primaryKey -o tsv)
az keyvault secret set \
  --vault-name <keyvault-name> \
  --name AzureMapsPrimaryKey \
  --value "$AZURE_MAPS_KEY"
```

### 2. Local Development

```bash
# Clone repository
git clone <repo-url>
cd epi-geo-chat

# Create virtual environment
conda create -n epi-geo-chat python=3.11 -y
conda activate epi-geo-chat

# Install dependencies
pip install -r requirements/base.txt

# Configure environment
cp .env.example .env
# Add your credentials to .env:
# - AZURE_OPENAI_ENDPOINT
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
# - GEOCATALOG_URL
# - GEOCATALOG_SCOPE
# - AZURE_MAPS_SUBSCRIPTION_KEY
# - CHROMA_CLIENT_URL                      (for RAG collection resolution)
# - APPLICATIONINSIGHTS_CONNECTION_STRING  (for observability)

# Test setup
python scripts/test_agent_framework.py
python scripts/test_stac.py
python scripts/test_geocoding.py
python scripts/test_workflow.py
```

---

## Project Structure

```
epi-geo-chat/
├── src/
│   ├── agents/              # Agent Framework agents
│   │   ├── agent_config.py
│   │   ├── agent_runners.py       # Agent execution with tracing
│   │   ├── query_parser.py
│   │   ├── geocoding_temporal.py
│   │   ├── stac_coordinator.py
│   │   ├── response_synthesizer.py
│   │   └── workflow.py            # Orchestration with workflow-level tracing
│   ├── stac/                # STAC & geocoding
│   │   ├── catalog_client.py
│   │   └── geocoding.py
│   ├── rag/                 # RAG components
│   │   ├── collection_resolver.py
│   │   └── vector_store.py
│   ├── code_executor/       # Code execution (planned)
│   └── utils/
│       ├── logging_config.py      # Logging infrastructure
│       └── observability.py       # OpenTelemetry tracing setup
│
├── tests/
│   ├── evaluation/          # Evaluation framework
│   │   ├── evaluate.py            # QueryEvaluator with accuracy/precision/recall/IoU
│   │   └── results.json           # Latest evaluation results
│   ├── unit/
│   │   ├── test_agent_framework.py
│   │   ├── test_catalog_client.py
│   │   └── test_geocoding.py
│   ├── fixtures/
│   │   ├── sample_queries.json    # Golden dataset (8 annotated queries)
│   │   └── env.py
│   └── conftest.py
│
├── scripts/
│   ├── test_workflow.py
│   ├── inventory_stac.py
│   └── index_collections.py
│
├── docs/                    # Documentation
│   ├── agent_architecture.md
│   ├── agent_framework.md
│   ├── evaluations.md
│   ├── observability.md
│   └── rag.md
├── docs_/                   # Design documents & analysis
├── notebooks/               # Exploration notebooks
├── data/                    # ChromaDB vector store data
│
├── requirements/
│   └── base.txt
│
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Current Status

### Completed

- 4-agent sequential workflow with structured outputs
- 3-tier geocoding (Local → Azure Maps → LLM)
- STAC catalog integration
- Logging infrastructure
- End-to-end testing
- Observability with Azure Monitor OpenTelemetry (per-agent tracing with argument/output capture)
- Evaluation framework with golden dataset (accuracy, precision, recall, bounding box IoU)
- Sub-intent classification in agent pipeline
- RAG collection resolver and vector store
- Agent execution refactored into `agent_runners.py` with traced decorators

### In Progress

- Unit and integration test coverage
- Documentation

### Planned

- FastAPI backend with REST API
- React frontend with map visualization
- Code generation and sandboxed execution
- User authentication
- Query history and caching

---

## Usage Examples

```python
from src.agents.workflow import process_query

# Run a query
result = await process_query("Show me rainfall in Lagos for February 2024")
print(result.final_response)
```

Expected output:
```
I found 28 CHIRPS rainfall measurements for Lagos in February 2024.
The data covers February 1-29, 2024. You can visualize this data
as a time series or calculate monthly averages.
```
---

## Contact

**Marouf Shaikh**
GitHub: MarShaikh

Inspired by [Microsoft Earth Copilot](https://github.com/microsoft/Earth-Copilot) (simplified from 13 to 4 agents).
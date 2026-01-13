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

**Future Components:**
- FastAPI backend
- React + TypeScript frontend
- ChromaDB for RAG
- Docker for code execution

### Agent Pipeline

```
User Query → Parser → Geocoder → STAC Search → Synthesizer → Response
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
│   │   ├── query_parser.py
│   │   ├── geocoding_temporal.py
│   │   ├── stac_coordinator.py
│   │   └── response_synthesizer.py
│   ├── stac/                # STAC & geocoding
│   │   ├── catalog_client.py
│   │   └── geocoding.py
│   ├── rag/                 # RAG (planned)
│   ├── code_executor/       # Code execution (planned)
│   └── utils/               # Logging, etc.
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── scripts/                 # Test scripts
│   ├── test_agent_framework.py
│   ├── test_stac.py
│   ├── test_geocoding.py
│   ├── test_workflow.py
│   └── inventory_stac.py
│
├── requirements/
│   └── base.txt
│
├── .env.example
└── README.md
```

---

## Current Status

### ✅ Completed

- 4-agent sequential workflow with structured outputs
- 3-tier geocoding (Local → Azure Maps → LLM)
- STAC catalog integration
- Logging infrastructure
- End-to-end testing

### 🚧 In Progress

- Unit test coverage
- Integration tests
- Documentation

### 📋 Planned (Phase 1)

- FastAPI backend with REST API
- React frontend with map visualization
- RAG integration with ChromaDB
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

## Framework Choice

**Microsoft Agent Framework** was chosen over Semantic Kernel and LangChain for:
- Native Azure OpenAI integration
- Built-in structured output support
- Function calling capabilities
- Microsoft's long-term support

Inspired by [Microsoft Earth Copilot](https://github.com/microsoft/Earth-Copilot) (simplified from 13 to 4 agents).

---

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## Contact

**Marouf Shaikh**
GitHub: MarShaikh

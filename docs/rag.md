# RAG: Collection Resolution with ChromaDB

The system uses Retrieval-Augmented Generation (RAG) with ChromaDB to semantically match user queries to relevant STAC collections.

## Overview

When a user asks about "rainfall" or "temperature", the RAG layer performs a semantic search against indexed STAC collection metadata to find the most relevant collection IDs (e.g., `Nigeria-CHIRPS`, `modis-11A1-061-nigeria`). This avoids hardcoding collection mappings and allows the system to scale as new collections are added to the catalog.

## Architecture

```
User Keywords → ChromaDB Semantic Search → Ranked Collection IDs → STAC API Query
```

## Components

### Vector Store (`src/rag/vector_store.py`)

The `CollectionVectorStore` class manages the ChromaDB collection for STAC metadata.

**Connection:**
- Connects to a ChromaDB HTTP server via `CHROMA_CLIENT_URL` environment variable (SSL enabled)
- Validates connection with a heartbeat check on initialization
- Uses a collection named `stac_collections`

**Indexing (`index_collections_from_api`):**

Fetches all collections from the GeoCatalog API and creates rich text embeddings from:
- Collection title and description
- Keywords (critical for matching user queries)
- License information

Each document is stored with metadata including:
- `collection_id` — STAC collection identifier
- `title` — Human-readable title
- `keywords` — Collection keywords
- `spatial_extent` — Bounding box coverage
- `temporal_extent` — Temporal range

**Querying (`query_collections`):**

Takes a list of user keywords, joins them into a single query string, and performs a semantic search against ChromaDB. Returns the top `n_results` collection IDs ranked by relevance.

```python
results = collection.query(query_texts=["rainfall precipitation"], n_results=3)
# Returns: ["Nigeria-CHIRPS", ...]
```

### Collection Resolver (`src/rag/collection_resolver.py`)

A convenience function that wraps the vector store for use in the agent workflow:

```python
from src.rag.collection_resolver import resolve_collections_by_keywords

collections = resolve_collections_by_keywords(
    data_type_keywords=["temperature", "thermal", "LST"],
    limit=3
)
# Returns: ['modis-11A1-061-nigeria-557', 'modis-11A2-061-nigeria']
```

### Indexing Script (`scripts/index_collections.py`)

A standalone script to populate the ChromaDB vector store from the GeoCatalog API:

```bash
python scripts/index_collections.py
```

This also runs test queries (rainfall, temperature, vegetation) to verify the semantic search is working correctly.

## Configuration

**Required environment variable:**
```
CHROMA_CLIENT_URL=<your-chromadb-host>
```

**Dependency:**
```
chromadb  # in requirements/base.txt
```

## How It Fits in the Pipeline

The RAG collection resolver is called during the agent workflow to map data type keywords extracted by the Query Parser (Agent 1) into concrete STAC collection IDs before passing them to the STAC Coordinator (Agent 3).

## ChromaDB Infrastructure on Azure Container Apps

ChromaDB is hosted as a Container App on Azure with persistent storage via Azure File Share.

### Azure Resources

| Resource | Name | Details |
|---|---|---|
| **Storage Account** | `mpcpstorageaccount` | Existing account in `rg_mpcp` |
| **Azure File Share** | `epi-geo-chromadb` | Persistent volume for ChromaDB data |
| **Container Apps Environment** | `epi-geo-container-env` | West Europe region |
| **Container App** | `chromadb-vector-store` | `chromadb/chroma:latest` image, 0.5 CPU / 1Gi RAM |

### Setup Steps

**1. Create the Azure File Share:**

```bash
az storage share create \
  --name epi-geo-chromadb \
  --account-name $STORAGE_ACCOUNT_NAME \
  --account-key $STORAGE_ACCOUNT_KEY
```

**2. Create the Container Apps Environment:**

```bash
az containerapp env create \
  --name $CONTAINER_ENVIRONMENT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location westeurope
```

**3. Register the file share as a storage definition in the environment:**

This tells the Container Apps Environment that the Azure File Share exists and apps can mount it.

```bash
az containerapp env storage set \
  --name $CONTAINER_ENVIRONMENT_NAME \
  --resource-group $RESOURCE_GROUP \
  --storage-name epi-geo-chromadb \
  --azure-file-account-name $STORAGE_ACCOUNT_NAME \
  --azure-file-account-key $STORAGE_ACCOUNT_KEY \
  --azure-file-share-name epi-geo-chromadb \
  --access-mode ReadWrite
```

> **Note:** The `--storage-name` is a reference name used in the container app deployment to identify the mount. The `--azure-file-share-name` must match the actual file share created in step 1. A mismatch here causes a `VolumeMountFailure` with exit code 1.

**4. Deploy the Container App:**

```bash
az containerapp create \
  --name chromadb-vector-store \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_ENVIRONMENT_NAME \
  --image chromadb/chroma:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 --max-replicas 1 \
  --cpu 0.5 --memory 1Gi
```

Key configuration:
- **Image:** `chromadb/chroma:latest` on port 8000
- **Ingress:** External, HTTPS only
- **Scale:** Fixed at 1 replica
- **Volume mount:** Azure File Share mounted at `/chroma/chroma` for data persistence
- **Revision mode:** Single (one active revision at a time)

**5. Verify the deployment with a health check:**

```bash
curl https://<FQDN>/api/v2/heartbeat
# Expected: {"nanosecond heartbeat": ...}
```

### Populating the Vector Store

After deployment, the ChromaDB instance must be indexed before the agent workflow can resolve collections:

```bash
python scripts/index_collections.py
```

This fetches all collections from the GeoCatalog API and indexes their metadata into the `stac_collections` ChromaDB collection. Re-run this script whenever new collections are added to the catalog.

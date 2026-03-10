# Local Development with Docker Compose

## Overview

This document explains the local development containerisation setup — what each file does, why it exists, and how to use it.

The goal is to give developers a single command (`docker compose up`) to run the full stack locally, matching the production topology as closely as possible while keeping the developer experience fast.

## Architecture

```
┌──────────────────────────────────────────────────┐
│  docker compose                                  │
│                                                  │
│  ┌─────────┐    ┌──────────┐    ┌──────────────┐ │
│  │ frontend│───►│ backend  │───►│ hosted       │ │
│  │ :5173   │    │ :8000    │    │ ChromaDB     │ │
│  └─────────┘    └────┬─────┘    │ (Azure)      │ │
│                      │          └──────────────┘ │
│                      │ Docker socket             │
│                      ▼                           │
│                 ┌──────────┐                     │
│                 │ sandbox  │ (spawned on demand) │
│                 │ container│                     │
│                 └──────────┘                     │
└──────────────────────────────────────────────────┘
```

**Key design decisions:**

- **ChromaDB is not containerised locally.** We use the hosted instance on Azure Container Apps (`CHROMA_CLIENT_URL` in `.env`). This avoids maintaining a local vector DB, keeps setup simple, and ensures the same indexed data is used everywhere.
- **The sandbox image is built but not run as a long-lived service.** The `sandbox` service in docker-compose exists only to build and tag the `epi-geo-sandbox:latest` image. The backend spawns sandbox containers on demand via the mounted Docker socket.
- **The frontend runs Vite's dev server inside the container**, with hot-reload working via the exposed port. For active frontend development, you can also run `npm run dev` natively (outside Docker) — the Vite proxy in `vite.config.ts` already points to `localhost:8000`.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- A `.env` file at the project root with the required environment variables (see [Environment Variables](#environment-variables))

## Quick Start

```bash
# Build and start all services
docker compose up --build

# Or in detached mode
docker compose up --build -d

# Check status
docker compose ps

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop everything
docker compose down
```

## Services

### backend

| Property | Value |
|----------|-------|
| **Image** | Built from `./Dockerfile` |
| **Base** | `python:3.12-slim` + GDAL system libraries |
| **Port** | `8000` → `8000` |
| **Health check** | `GET /health` |

The backend Dockerfile installs system-level GDAL/geospatial dependencies, then Python packages from `requirements/base.txt`, then copies the application source. The layer ordering is intentional — Python dependencies change less often than source code, so Docker can cache the expensive `pip install` layer.

The Docker socket (`/var/run/docker.sock`) is mounted as a volume so the backend can spawn sandbox containers for code execution.

The `~/.azure` directory is mounted so `DefaultAzureCredential` can use your local Azure CLI login to authenticate with GeoCatalog. You must be logged in via `az login` before starting the containers.

#### Sandbox volume mounting (sibling container pattern)

When the backend runs inside Docker and spawns sandbox containers via the Docker socket, it creates **sibling containers** — not child containers. This means bind mount paths in `volumes` must be resolvable by the Docker daemon on the **host**, not inside the backend container.

To solve this, both the backend container and sandbox containers share a host-visible temp directory (`/tmp/epi-sandbox`). The `SANDBOX_TEMP_DIR` env var tells the backend to create temp files there instead of the default system temp dir. Since this directory is bind-mounted at the same path in the backend container, the paths the backend passes to `docker.containers.run(volumes=...)` are valid on the host.

When running the backend **natively** (outside Docker), `SANDBOX_TEMP_DIR` is unset, so `tempfile.mkdtemp()` uses the default system temp dir — no change in behaviour.

### frontend

| Property | Value |
|----------|-------|
| **Image** | Built from `frontend/Dockerfile` |
| **Base** | `node:22-slim` |
| **Port** | `5173` → `5173` |

Runs Vite's dev server with `--host 0.0.0.0` so it's accessible from outside the container. The Vite proxy configuration in `vite.config.ts` forwards `/api/*` and `/health` requests to `localhost:8000`.

**Note:** When running the frontend inside Docker but the backend also inside Docker, the Vite proxy target `localhost:8000` works because the backend binds to the host's port 8000. If you ever change this, update `vite.config.ts` accordingly.

### sandbox

| Property | Value |
|----------|-------|
| **Image** | Built from `src/code_executor/docker/Dockerfile`, tagged as `epi-geo-sandbox:latest` |
| **Purpose** | Build-only — exits immediately after image is built |

This service doesn't run continuously. It exists so that `docker compose build` (or `docker compose up --build`) builds and tags the sandbox image. The backend then uses this image when spawning code execution containers.

The `depends_on` condition ensures the sandbox image is built before the backend starts.

## Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Backend container image — Python 3.12 + GDAL + app source |
| `.dockerignore` | Excludes `.git`, `node_modules`, `.env`, tests, etc. from Docker build context |
| `frontend/Dockerfile` | Frontend dev server — Node 22 + Vite |
| `frontend/.dockerignore` | Excludes `node_modules` and `dist` from frontend build context |
| `docker-compose.yml` | Orchestrates all three services |

## Environment Variables

The backend reads its configuration from `.env` at the project root. Key variables:

```
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT_NAME=...
AZURE_OPENAI_API_VERSION=preview
AZURE_GEOCATALOG_ENDPOINT=...
AZURE_MAPS_SUBSCRIPTION_KEY=...
CHROMA_CLIENT_URL=https://<your-chromadb>.azurecontainerapps.io
APPLICATIONINSIGHTS_CONNECTION_STRING=...   # optional
```

The `.env` file is **not** copied into the Docker image (it's in `.dockerignore`). Instead, it's passed at runtime via `env_file: .env` in docker-compose. This keeps secrets out of the image layers.

## Hybrid Development (Recommended for Frontend Work)

For active frontend development, running Vite natively gives you faster hot-reload:

```bash
# Start only the backend in Docker
docker compose up backend

# Run frontend natively
cd frontend && npm run dev
```

The Vite dev server at `localhost:5173` proxies API calls to `localhost:8000` (the dockerised backend).

## Troubleshooting

### Backend keeps restarting
Check logs with `docker compose logs backend`. Common causes:
- Missing `.env` file or missing required environment variables
- Python version mismatch — the backend uses Python 3.12 features (e.g. nested f-string quotes). The Dockerfile uses `python:3.12-slim` for this reason.

### Sandbox containers fail to spawn
The backend needs access to the Docker socket. Verify:
```bash
docker compose exec backend ls -la /var/run/docker.sock
```
On macOS with Docker Desktop, this should work out of the box.

### Frontend can't reach backend
The Vite proxy forwards to `localhost:8000`. Ensure the backend is running and healthy:
```bash
curl http://localhost:8000/health
```

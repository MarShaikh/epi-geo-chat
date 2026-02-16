"""Health check endpoints."""

import os

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Liveness probe."""
    return {"status": "healthy", "version": "0.1.0"}


@router.get("/health/ready")
async def readiness_check():
    """Readiness probe - checks downstream dependencies."""
    services = {}

    try:
        import chromadb
        client = chromadb.HttpClient(
            host=os.environ["CHROMA_CLIENT_URL"], ssl=True
        )
        client.heartbeat()
        services["chromadb"] = "ok"
    except Exception as e:
        services["chromadb"] = f"error: {e}"

    all_ok = all(v == "ok" for v in services.values())
    return {
        "status": "ready" if all_ok else "degraded",
        "services": services,
    }

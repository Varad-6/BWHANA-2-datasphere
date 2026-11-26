"""BW Morph FastAPI Application Entry Point."""

from datetime import datetime, timezone
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import get_settings
from api.routers import classify, generate, graph, health, repository, scan

settings = get_settings()

app = FastAPI(
    title="BW Morph Migration Accelerator API",
    description="REST API layer for SAP BW/4HANA to SAP Datasphere migration (Tools T0-T12).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return structured error responses instead of raw tracebacks."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "code": "INTERNAL_SERVER_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


app.include_router(health.router, prefix="/api/v1")
app.include_router(scan.router, prefix="/api/v1")
app.include_router(repository.router, prefix="/api/v1")
app.include_router(graph.router, prefix="/api/v1")
app.include_router(classify.router, prefix="/api/v1")
app.include_router(generate.router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )

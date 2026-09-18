import logging
import time

from fastapi import FastAPI, Request

from app.api.routes import documents, health, query
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()
logger = logging.getLogger("docmind.http")

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Document ingestion and citation-aware RAG API using PostgreSQL + pgvector.",
)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "%s %s -> %s %.1fms",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


app.include_router(health.router)
app.include_router(documents.router, prefix="/api/v1")
app.include_router(query.router, prefix="/api/v1")

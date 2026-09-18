from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.query_log import QueryLog
from app.schemas.query import QueryHistoryRead, QueryRequest, QueryResponse
from app.services.rag import generate_answer, retrieve_sources

router = APIRouter(tags=["rag"])


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    payload: QueryRequest,
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
    sources = await retrieve_sources(payload.question, payload.top_k, db)
    answer = await generate_answer(payload.question, sources)

    log = QueryLog(
        question=payload.question,
        answer=answer,
        sources=[source.model_dump(mode="json") for source in sources],
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)

    return QueryResponse(query_id=log.id, answer=answer, sources=sources)


@router.get("/queries", response_model=list[QueryHistoryRead])
async def query_history(db: AsyncSession = Depends(get_db)) -> list[QueryLog]:
    result = await db.execute(select(QueryLog).order_by(QueryLog.id.desc()).limit(100))
    return list(result.scalars().all())

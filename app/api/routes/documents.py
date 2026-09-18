import hashlib

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.document import Chunk, Document
from app.schemas.document import DocumentRead
from app.services.chunking import chunk_text
from app.services.embeddings import embed_texts
from app.services.parser import UnsupportedDocumentError, extract_text

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> Document:
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    digest = hashlib.sha256(data).hexdigest()
    existing = await db.scalar(select(Document).where(Document.sha256 == digest))
    if existing is not None:
        raise HTTPException(status_code=409, detail="This document has already been indexed")

    try:
        text = extract_text(file.filename or "document", data)
    except UnsupportedDocumentError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc

    if not text:
        raise HTTPException(status_code=422, detail="No extractable text was found")

    pieces = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
    vectors = await embed_texts(pieces)

    document = Document(
        filename=file.filename or "document",
        content_type=file.content_type or "application/octet-stream",
        sha256=digest,
        chunk_count=len(pieces),
    )
    db.add(document)
    await db.flush()

    db.add_all(
        [
            Chunk(
                document_id=document.id,
                position=index,
                content=piece,
                embedding=vector,
            )
            for index, (piece, vector) in enumerate(zip(pieces, vectors, strict=True))
        ]
    )
    await db.commit()
    await db.refresh(document)
    return document


@router.get("", response_model=list[DocumentRead])
async def list_documents(db: AsyncSession = Depends(get_db)) -> list[Document]:
    result = await db.execute(select(Document).order_by(Document.id.desc()))
    return list(result.scalars().all())


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)) -> Document:
    document = await db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
) -> Response:
    document = await db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    await db.delete(document)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), index=True)
    content_type: Mapped[str] = mapped_column(String(100))
    sha256: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    chunk_count: Mapped[int] = mapped_column(Integer(), default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer())
    content: Mapped[str] = mapped_column(Text())
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embedding_dimensions))

    document: Mapped[Document] = relationship(back_populates="chunks")

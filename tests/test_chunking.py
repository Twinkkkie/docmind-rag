import pytest

from app.services.chunking import chunk_text


def test_chunk_text_preserves_content_and_overlap() -> None:
    text = " ".join(f"token{i}" for i in range(100))
    chunks = chunk_text(text, chunk_size=120, overlap=20)

    assert len(chunks) > 1
    assert all(chunks)
    assert all(len(chunk) <= 120 for chunk in chunks)


def test_chunk_text_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        chunk_text("hello world", chunk_size=10, overlap=10)

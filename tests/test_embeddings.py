from app.services.embeddings import deterministic_embedding


def test_deterministic_embedding_is_stable_and_normalized() -> None:
    first = deterministic_embedding("Python FastAPI pgvector", 64)
    second = deterministic_embedding("Python FastAPI pgvector", 64)

    assert first == second
    norm = sum(value * value for value in first) ** 0.5
    assert abs(norm - 1.0) < 1e-9


def test_empty_embedding_is_zero_vector() -> None:
    assert deterministic_embedding("", 8) == [0.0] * 8

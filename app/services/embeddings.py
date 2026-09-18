import hashlib
import math
import re

from langchain_openai import OpenAIEmbeddings

from app.core.config import settings


def deterministic_embedding(text: str, dimensions: int) -> list[float]:
    vector = [0.0] * dimensions
    for token in re.findall(r"\w+", text.lower(), flags=re.UNICODE):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    if settings.openai_api_key:
        embedder = OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
            dimensions=settings.embedding_dimensions,
        )
        return await embedder.aembed_documents(texts)

    return [
        deterministic_embedding(text, settings.embedding_dimensions)
        for text in texts
    ]


async def embed_query(text: str) -> list[float]:
    if settings.openai_api_key:
        embedder = OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
            dimensions=settings.embedding_dimensions,
        )
        return await embedder.aembed_query(text)

    return deterministic_embedding(text, settings.embedding_dimensions)

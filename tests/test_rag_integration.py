import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_text_ingestion_query_and_delete() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        uploaded = await client.post(
            "/api/v1/documents",
            files={
                "file": (
                    "guide.txt",
                    b"AgentDesk uses explicit human approval before AI actions are executed.",
                    "text/plain",
                )
            },
        )
        assert uploaded.status_code == 201
        document = uploaded.json()
        assert document["chunk_count"] == 1

        queried = await client.post(
            "/api/v1/query",
            json={"question": "What happens before AI actions are executed?", "top_k": 3},
        )
        assert queried.status_code == 200
        result = queried.json()
        assert result["sources"]
        assert result["sources"][0]["citation"].startswith("[D")

        deleted = await client.delete(f"/api/v1/documents/{document['id']}")
        assert deleted.status_code == 204

from fastapi.testclient import TestClient
from app.main import app
import pytest
import asyncio
import time
import httpx
from httpx import AsyncClient

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    

    assert response.status_code == 200
    

    data = response.json()
    

    assert data["status"] == "healthy"
    

    assert "database_connected" in data
    assert "timestamp" in data

@pytest.mark.asyncio
async def test_concurrent_requests_are_non_blocking():
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        start_time = time.time()
        
        results = await asyncio.gather(
            client.get("/health"),
            client.get("/health")
        )
        
        assert (time.time() - start_time) < 2


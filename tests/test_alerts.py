import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.ws_manager import manager
import asyncio

client = TestClient(app)

@pytest.mark.asyncio
async def test_websocket_connection_and_broadcast():
    with client.websocket_connect("/ws/alerts") as websocket:
        async def mock_broadcast():
            await asyncio.sleep(0.1)
            await manager.broadcast_anomaly("1234-5678", "Critical anomaly detected")
            
        asyncio.create_task(mock_broadcast())
        
        data = websocket.receive_json()
        assert data["type"] == "anomaly_alert"
        assert data["patient_id"] == "1234-5678"
        assert data["message"] == "Critical anomaly detected"
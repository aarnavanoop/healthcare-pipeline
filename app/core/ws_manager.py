from fastapi import WebSocket
from typing import List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_anomaly(self, patient_id: str, message: str):
        payload = json.dumps({
            "patient_id": str(patient_id),
            "message": message,
            "type": "anomaly_alert"
        })
        for connection in self.active_connections:
            await connection.send_text(payload)

manager = ConnectionManager()
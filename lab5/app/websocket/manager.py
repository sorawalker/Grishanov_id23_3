import json
from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        print(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                print(f"User {user_id} disconnected. Remaining connections: {len(self.active_connections[user_id])}")
                
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            disconnected_connections = []
            
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    print(f"Error sending message to user {user_id}: {e}")
                    disconnected_connections.append(connection)
            
            for connection in disconnected_connections:
                self.disconnect(connection, user_id)
    
    async def send_notification(self, user_id: int, notification: dict):
        message = json.dumps(notification)
        await self.send_personal_message(message, user_id)
    
    def get_user_connections_count(self, user_id: int) -> int:
        return len(self.active_connections.get(user_id, []))
    
    def get_total_connections(self) -> int:
        return sum(len(connections) for connections in self.active_connections.values())


manager = ConnectionManager() 
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.websocket.manager import manager
from app.core.security import verify_token
from app.cruds import user as user_crud
from app.db.database import get_db

router = APIRouter()


async def get_user_from_token(
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is required"
        )
    
    user_id = verify_token(token)
    user = user_crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        try:
            user_id = verify_token(token)
            user = user_crud.get_user(db, user_id=user_id)
            if user is None:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
        except Exception:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        await manager.connect(websocket, user_id)
        
        await manager.send_notification(user_id, {
            "status": "CONNECTED",
            "message": f"Connected to WebSocket channel for user {user_id}"
        })
        
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    await manager.send_notification(user_id, {
                        "status": "ECHO",
                        "message": f"Received message: {message}"
                    })
                except json.JSONDecodeError:
                    await manager.send_notification(user_id, {
                        "status": "ERROR",
                        "message": "Invalid JSON format"
                    })
                    
        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id)
            print(f"User {user_id} disconnected from WebSocket")
            
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass


@router.get("/ws/status")
async def websocket_status():
    return {
        "total_connections": manager.get_total_connections(),
        "active_users": len(manager.active_connections)
    } 
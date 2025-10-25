from fastapi import APIRouter, WebSocket, Depends, HTTPException, Query
from app.websocket_manager import websocket_endpoint
from app.auth import get_current_active_user
from app.models import User

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_route(
    websocket: WebSocket,
    user_id: str = Query(..., description="사용자 ID")
):
    """WebSocket 연결 엔드포인트"""
    await websocket_endpoint(websocket, user_id)

from fastapi import APIRouter
from app.api.v1.endpoints import auth, game, ws

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(game.router, prefix="/game", tags=["game"])
api_router.include_router(ws.router, tags=["websocket"])
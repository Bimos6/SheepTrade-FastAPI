from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.game import (
    BetRequest, BetResponse, SellResponse,
    InventoryItemResponse, SheepTemplateResponse, BetHistoryResponse
)
from app.services.game_service import GameService

router = APIRouter()

@router.post("/bet", response_model=BetResponse)
@limiter.limit("7/minute")
async def make_bet(
    request: Request, 
    bet_data: BetRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    service = GameService(db)
    result = await service.proccess_bet(current_user.id, bet_data.amount)
    return result

@router.post("/sell/{inventory_id}", response_model=SellResponse)
async def sell_sheep(
    inventory_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    service = GameService(db)
    result = await service.sell_sheep(current_user.id, inventory_id)
    return result

@router.get("/inventory", response_model=list[InventoryItemResponse])
async def get_my_inventory(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    service = GameService(db)
    return await service.get_inventory(current_user.id)

@router.get("/sheep-types", response_model=list[SheepTemplateResponse])
async def get_sheep_types(
    db: Annotated[AsyncSession, Depends(get_db)]
):
    service = GameService(db)
    return await service.get_sheep_templates()

@router.get("/history", response_model=list[BetHistoryResponse])
async def get_history(
    db: Annotated[AsyncSession, Depends(get_db)]
):
    service = GameService(db)
    return await service.get_bet_history()
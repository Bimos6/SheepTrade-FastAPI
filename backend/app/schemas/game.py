from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.user import UserResponse

class BetRequest(BaseModel):
    amount: int = Field(..., ge=1, description="Сумма ставки (минимум 1)")

class RolledSheepResponse(BaseModel):
    inventory_id: int
    sheep_name: str
    rarity: str
    drop_chance: float
    purchase_price: int
    current_price: int

class BetResponse(BaseModel):
    user: UserResponse
    rolled_sheep: RolledSheepResponse

class SellResponse(BaseModel):
    message: str
    earned_amount: int
    new_balance: int

class InventoryItemResponse(BaseModel):
    inventory_id: int
    sheep_name: str
    rarity: str
    purchase_price: int
    current_price: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SheepTemplateResponse(BaseModel):
    id: int
    name: str
    rarity: str
    base_chance: float
    base_min_price: int
    base_max_price: int

    model_config = ConfigDict(from_attributes=True)

class BetHistoryResponse(BaseModel):
    id: int
    username: str
    amount: int
    sheep_name: str
    rarity: str
    created_at: datetime

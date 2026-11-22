import random
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select

from app.repositories.user_repo import UserRepository
from app.models.sheep import Sheep
from app.models.inventory import Inventory
from app.models.bet import Bet
from app.models.user import User
from app.core.game_config import BOOST_SCALES
from app.core.ws_manager import manager

class GameService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
    
    def _roll_dynamic(self, sheep_list: list[Sheep], bet_amount: int):
        bet_factor = bet_amount / 10.0

        total_added = 0.0
        chances = []

        for s in sheep_list:
            scale = BOOST_SCALES.get(s.rarity, 0.0)
            added = scale * bet_factor
            total_added += added
            chances.append(s.base_chance + added)
        
        chances[0] = max(0.1, chances[0] - total_added)

        total = sum(chances)
        normalized_chances = [c / total for c in chances]

        rand = random.random()
        cumulative = 0.0
        for i, chance in enumerate(normalized_chances):
            cumulative += chance
            if rand <= cumulative:
                return sheep_list[i], chance * 100
        
        return sheep_list[0], normalized_chances[0] * 100

    async def proccess_bet(self, user_id: int, amount: int):
        try:
            user = await self.user_repo.get_for_update(user_id)

            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            
            if user.balance < amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Недостаточно средств на балансе"
                )

            user.balance -= amount

            result = await self.session.execute(select(Sheep).order_by(Sheep.base_chance.desc()))
            all_sheep = result.scalars().all()

            if not all_sheep:
                raise HTTPException(status_code=500, detail="Справочник овец пуст")

            template, drop_chance = self._roll_dynamic(all_sheep, amount)
            current_price = random.randint(template.base_min_price, template.base_max_price)

            inventory_item = Inventory(
                user_id=user.id,
                sheep_id=template.id,
                purchase_price=current_price,
                current_price=current_price
            )
            self.session.add(inventory_item)
            await self.session.flush()

            bet_log = Bet(
                user_id=user_id,
                amount=amount,
                dropped_sheep_id=template.id
            )
            self.session.add(bet_log)

            await self.session.commit()

            ws_message = {
                "type": "new_bet",
                "username": user.username,
                "amount": amount,
                "sheep_name": template.name,
                "rarity": template.rarity,
                "drop_chance": round(drop_chance, 2)
            }
            await manager.broadcast(ws_message)

            return {
                "user": user,
                "rolled_sheep": {
                    "inventory_id": inventory_item.id,
                    "sheep_name": template.name,
                    "rarity": template.rarity,
                    "drop_chance": round(drop_chance, 2),
                    "purchase_price": current_price,
                    "current_price": current_price
                }
            }
        except Exception as e:
            await self.session.rollback()
            raise e

    async def sell_sheep(self, user_id: int, inventory_id: int):
        try:
            user = await self.user_repo.get_for_update(user_id)

            if not user:
                raise HTTPException(status_code404, detail="Пользователь не найден")

            result = await self.session.execute(
                select(Inventory).where(
                    Inventory.id == inventory_id,
                    Inventory.user_id == user_id
                )
            )
            item = result.scalar_one_or_none()

            if not item:
                raise HTTPException(status_code=404, detail="Овца не найдена в вашем амбаре")
            
            earned = item.current_price
            user.balance += earned

            await self.session.delete(item)

            await self.session.commit()

            return {
                "message": "Овца успешно продана",
                "earned_amount": earned,
                "new_balance": user.balance
            }
        except Exception as e:
            await self.session.rollback()
            raise e
        
    async def get_inventory(self, user_id: int):
        query = (
            select(Inventory, Sheep)
            .join(Sheep, Inventory.sheep_id == Sheep.id)
            .order_by(Inventory.created_at.desc())
        )
        result = await self.session.execute(query)
        items = result.all()

        return [
            {
                "inventory_id": inv.id,
                "sheep_name": sheep.name,
                "rarity": sheep.rarity,
                "purchase_price": inv.purchase_price,
                "current_price": inv.current_price,
                "created_at": inv.created_at
            }
            for inv, sheep in items
        ]

    async def get_sheep_templates(self):
        result = await self.session.execute(select(Sheep).order_by(Sheep.base_chance.desc()))
        return result.scalars().all()

    async def get_bet_history(self, limit: int = 15):
        query = (
            select(Bet, User.username, Sheep.name, Sheep.rarity)
            .join(User, Bet.user_id == User.id)
            .join(Sheep, Bet.dropped_sheep_id == Sheep.id)
            .order_by(Bet.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        items = result.all()

        return [
            {
                "id": bet.id,
                "username": username,
                "amount": bet.amount,
                "sheep_name": sheep_name,
                "rarity": rarity,
                "created_at": bet.created_at
            }
            for bet, username, sheep_name, rarity in items
        ]
import random
from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.inventory import Inventory
from app.models.sheep import Sheep

async def update_market_price(ctx):
    print("Фоновая задача: пересчет рыночных цен овец...")

    async with async_session_maker() as session:
        result = await session.execute(select(Inventory))
        items = result.scalars().all()

        if not items:
            return
        
        for item in items:
            # Берем базовую цену овцы, чтобы цена не улетела в космос
            # (В реальном проекте лучше сделать отдельную таблицу с историей цен)
            # Для простоты берем текущую цену и меняем её на +/- 10%
            fluctuation = random.uniform(0.9, 1.1)
            new_price = int(item.current_price * fluctuation)

            if new_price < 1:
                new_price = 1

            item.current_price = new_price
        
        await session.commit()
        print(f"Цены обновленны для {len(items)} овец.")
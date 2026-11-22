import asyncio
from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.sheep import Sheep

SHEEP_DATA = [
    {"name": "Овечка Обычная", "rarity": "Обычный", "base_min_price": 100, "base_max_price": 500, "base_chance": 45.0},
    {"name": "Овечка Необычная", "rarity": "Необычный", "base_min_price": 500, "base_max_price": 1500, "base_chance": 25.0},
    {"name": "Овечка Редкая", "rarity": "Редкий", "base_min_price": 1500, "base_max_price": 5000, "base_chance": 15.0},
    {"name": "Овечка Эпическая", "rarity": "Эпический", "base_min_price": 5000, "base_max_price": 15000, "base_chance": 8.0},
    {"name": "Овечка Легендарная", "rarity": "Легендарный", "base_min_price": 15000, "base_max_price": 50000, "base_chance": 4.0},
    {"name": "Овечка Мифическая", "rarity": "Мифический", "base_min_price": 50000, "base_max_price": 150000, "base_chance": 2.0},
    {"name": "Овечка Древняя", "rarity": "Древний", "base_min_price": 150000, "base_max_price": 500000, "base_chance": 0.7},
    {"name": "Овечка Космическая", "rarity": "Космический", "base_min_price": 500000, "base_max_price": 1500000, "base_chance": 0.2},
    {"name": "Овечка Божественная", "rarity": "Божественный", "base_min_price": 1500000, "base_max_price": 5000000, "base_chance": 0.08},
    {"name": "Овечка Сезонная", "rarity": "Сезонный", "base_min_price": 5000000, "base_max_price": 10000000, "base_chance": 0.02},
]

async def seed_sheep():
    async with async_session_maker() as session:
        result = await session.execute(select(Sheep))
        if result.scalars().first():
            print("Справочник овец уже заполнен.")
            return
        
        for data in SHEEP_DATA:
            sheep = Sheep(**data)
            session.add(sheep)

        await session.commit()
        print("Справочник овец успешно заполнен!")

if __name__ == "__main__":
    asyncio.run(seed_sheep())
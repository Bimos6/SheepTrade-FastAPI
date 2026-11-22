from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Sheep(Base):
    __tablename__ = "sheep"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rarity: Mapped[str] = mapped_column(String(50), nullable=False)
    base_min_price: Mapped[int] = mapped_column(Integer, nullable=False)
    base_max_price: Mapped[int] = mapped_column(Integer, nullable=False)
    base_chance: Mapped[float] = mapped_column(Float, nullable=False, default=0)
from datetime import datetime
from sqlalchemy import  BigInteger, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    balance: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    inventory: Mapped[list["Inventory"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    bets: Mapped[list["Bet"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
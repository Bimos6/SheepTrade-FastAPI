from datetime import datetime
from sqlalchemy import BigInteger, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sheep_id: Mapped[int] = mapped_column(Integer, ForeignKey("sheep.id"), nullable=False)

    purchase_price: Mapped[int] = mapped_column(Integer, nullable=False)
    current_price: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(back_populates="inventory")
    sheep: Mapped["Sheep"] = relationship()
from datetime import datetime
from sqlalchemy import BigInteger, SmallInteger, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class LikeModel(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint('user_id', 'target_type', 'target_id'),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    target_type: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    target_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

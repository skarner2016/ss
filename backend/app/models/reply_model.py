from datetime import datetime
from sqlalchemy import BigInteger, Text, SmallInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class ReplyModel(Base):
    __tablename__ = "replies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    comment_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reply_to_user_id: Mapped[int | None] = mapped_column(BigInteger)
    content_type: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

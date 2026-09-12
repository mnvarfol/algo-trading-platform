from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from storage.base import Base


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = {"schema": "alor"}  # noqa: RUF012

    id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(String, unique=True)
    refresh_token: Mapped[str] = mapped_column(String)
    refresh_token_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")

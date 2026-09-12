from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from storage.base import Base


class Portfolio(Base):
    __tablename__ = "portfolios"
    __table_args__ = (
        UniqueConstraint("account_id", "portfolio", "exchange"),
        {"schema": "alor"}
      )

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("alor.accounts.id"))
    portfolio: Mapped[str] = mapped_column(String(10))
    exchange: Mapped[str] = mapped_column(String(10))
    portfolio_value: Mapped[Decimal | None] = mapped_column(Numeric)
    risk_category_id: Mapped[int | None] = mapped_column(SmallInteger)
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")

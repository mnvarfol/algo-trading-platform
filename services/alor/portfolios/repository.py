from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from storage.postgres import PostgresConnection

from portfolios.models import Portfolio


class PortfolioRepository:

    def __init__(self, postgres: PostgresConnection):
        self._postgres = postgres

    async def get_active(self) -> list[Portfolio]:
        async with AsyncSession(self._postgres.engine) as session:
            result = await session.execute(select(Portfolio).where(Portfolio.is_active))
            return list(result.scalars().all())

    async def update_portfolio_value(
        self,
        portfolio_id: int,
        portfolio_value: Decimal,
    ) -> None:
        async with AsyncSession(self._postgres.engine) as session:
            await session.execute(
                update(Portfolio)
                .where(Portfolio.id == portfolio_id)
                .values(portfolio_value=portfolio_value)
            )
            await session.commit()

    async def update_risk_category_id(
        self,
        portfolio_id: int,
        risk_category_id: int,
    ) -> None:
        async with AsyncSession(self._postgres.engine) as session:
            await session.execute(
                update(Portfolio)
                .where(Portfolio.id == portfolio_id)
                .values(risk_category_id=risk_category_id)
            )
            await session.commit()

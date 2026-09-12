from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from storage.postgres import PostgresConnection

from portfolios.models import Portfolio


class PortfolioRepository:

    def __init__(self, postgres: PostgresConnection):
        self._postgres = postgres

    async def get_active(self) -> list[Portfolio]:
        async with AsyncSession(self._postgres.engine) as session:
            result = await session.execute(
                select(Portfolio).where(
                    Portfolio.is_active
                )
            )
            return list(result.scalars().all())
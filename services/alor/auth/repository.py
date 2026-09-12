from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from storage.postgres import PostgresConnection

from auth.models import Account


class AccountRepository:

    def __init__(self, postgres: PostgresConnection):
        self._postgres = postgres

    async def get_active(self) -> list[Account]:
        async with AsyncSession(self._postgres.engine) as session:
            result = await session.execute(
                select(Account).where(
                    Account.is_active,
                    Account.refresh_token_expires_at > datetime.now(UTC),
                )
            )
            return list(result.scalars().all())

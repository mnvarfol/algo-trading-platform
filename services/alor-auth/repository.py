from models import Account
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from storage.postgres import PostgresConnection


class AccountRepository:

    def __init__(self, postgres: PostgresConnection):
        self._postgres = postgres

    async def get_active_accounts(self) -> list[Account]:
        async with AsyncSession(self._postgres.engine) as session:
            result = await session.execute(select(Account).where(Account.is_active))
            return list(result.scalars().all())

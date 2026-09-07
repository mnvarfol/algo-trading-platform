import os

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def build_url(host: str, port: int, user: str, password: str, database: str) -> URL:
    return URL.create(
        drivername="postgresql+asyncpg",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
    )


class PostgresConnection:

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
    ):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self._engine: AsyncEngine | None = None

    @classmethod
    def from_env(cls) -> PostgresConnection:
        return cls(
            host=os.environ["POSTGRES_HOST"],
            port=int(os.environ["POSTGRES_PORT"]),
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            database=os.environ["POSTGRES_DB"],
        )

    async def init(self) -> None:
        url = build_url(self._host, self._port, self._user, self._password, self._database)
        self._engine = create_async_engine(url)

    async def close(self) -> None:
        if self._engine:
            await self._engine.dispose()
        self._engine = None

    @property
    def engine(self) -> AsyncEngine:
        if not self._engine:
            raise RuntimeError("Postgres engine is not initialized")
        return self._engine

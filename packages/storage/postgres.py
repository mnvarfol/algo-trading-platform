from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


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

    async def init(self) -> None:
        url = (
            f"postgresql+asyncpg://{self._user}:{self._password}"
            f"@{self._host}:{self._port}/{self._database}"
        )
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

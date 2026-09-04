import asyncpg
from asyncpg import Pool


class PostgresConnection:

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        min_size: int = 1,
        max_size: int = 10,
    ):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self._min_size = min_size
        self._max_size = max_size
        self._pool: Pool | None = None

    async def init(self) -> None:
        self._pool = await asyncpg.create_pool(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            database=self._database,
            min_size=self._min_size,
            max_size=self._max_size,
        )

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
        self._pool = None

    @property
    def pool(self) -> Pool:
        if not self._pool:
            raise RuntimeError("Postgres pool is not initialized")
        return self._pool

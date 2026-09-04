import redis.asyncio as redis
from redis.asyncio import Redis


class RedisConnection:

    def __init__(
        self,
        host: str,
        port: int,
        password: str,
        db: int = 0,
        max_connections: int = 20,
    ):
        self._host = host
        self._port = port
        self._password = password
        self._db = db
        self._max_connections = max_connections
        self._client: Redis | None = None

    async def init(self) -> None:
        self._client = redis.Redis(
            host=self._host,
            port=self._port,
            password=self._password,
            db=self._db,
            max_connections=self._max_connections,
            decode_responses=True,
        )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
        self._client = None

    @property
    def client(self) -> Redis:
        if not self._client:
            raise RuntimeError("Redis client is not initialized")
        return self._client

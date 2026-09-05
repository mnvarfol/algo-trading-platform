from storage.redis import RedisConnection


class TokenService:

    def __init__(self, redis: RedisConnection):
        self._redis = redis

    async def get_access_token(self, portfolio: str) -> str | None:
        value = await self._redis.client.get(f"token:alor:access:{portfolio}")
        if isinstance(value, bytes):
            return value.decode()
        return value

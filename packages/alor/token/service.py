from storage.redis import RedisConnection

from .keys import access_token_key


class TokenService:

    def __init__(self, redis: RedisConnection):
        self._redis = redis

    async def get_access_token(self, account_id: int) -> str | None:
        value = await self._redis.client.get(access_token_key(account_id))
        if isinstance(value, bytes):
            return value.decode()
        return value

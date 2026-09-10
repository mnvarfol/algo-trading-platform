import pytest
from storage.redis import RedisConnection


@pytest.fixture
async def redis_connection():
    connection = RedisConnection.from_env()
    await connection.init()
    yield connection
    await connection.close()


async def test_set_and_get_roundtrip(redis_connection: RedisConnection):
    await redis_connection.client.set("test:roundtrip", "value", ex=5)

    value = await redis_connection.client.get("test:roundtrip")

    assert value == "value"

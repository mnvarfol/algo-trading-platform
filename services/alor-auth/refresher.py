import asyncio
import logging

from alor.client.http.auth import AuthClient
from alor.token.keys import access_token_key
from cryptography.fernet import Fernet
from encryption import decrypt_token
from models import Account
from repository import AccountRepository
from storage.redis import RedisConnection

logger = logging.getLogger(__name__)

ACCESS_TOKEN_TTL = 30 * 60


class TokenRefresher:

    def __init__(
        self,
        repository: AccountRepository,
        auth_client: AuthClient,
        redis: RedisConnection,
        encryption_key: str,
    ):
        self._repository = repository
        self._auth_client = auth_client
        self._redis = redis
        self._fernet = Fernet(encryption_key)

    async def refresh_all(self) -> None:
        accounts = await self._repository.get_active_accounts()
        results = await asyncio.gather(
            *(self._refresh_account(account) for account in accounts),
            return_exceptions=True,
        )
        for account, result in zip(accounts, results, strict=True):
            if isinstance(result, BaseException):
                logger.error(
                    "Failed to refresh token for account %s", account.tag, exc_info=result
                )

    async def _refresh_account(self, account: Account) -> None:
        refresh_token = decrypt_token(self._fernet, account.refresh_token)
        access_token = await self._auth_client.refresh_access_token(refresh_token)
        await self._redis.client.set(
            access_token_key(account.id),
            access_token,
            ex=ACCESS_TOKEN_TTL,
        )
        logger.info("Refreshed access token for account %s", account.tag)

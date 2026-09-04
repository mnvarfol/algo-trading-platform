from ..config import Config
from .exceptions import HttpError
from .transport import HttpTransport


class AuthClient:

    def __init__(self, transport: HttpTransport, config: Config):
        self._transport = transport
        self._config = config

    async def refresh_access_token(self, refresh_token: str) -> str:
        data = await self._transport.post(
            self._config.auth_url,
            params={"token": refresh_token},
        )
        if not isinstance(data, dict):
            raise HttpError("Unexpected response shape")

        access_token = data.get("AccessToken")
        if not access_token:
            raise HttpError("No AccessToken in response")
        return access_token

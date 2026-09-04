from aiohttp import ClientConnectionError, ClientSession

from .exceptions import HttpError


class HttpTransport:

    def __init__(self):
        self._session: ClientSession | None = None

    async def init(self) -> None:
        self._session = ClientSession()

    async def close(self) -> None:
        if self._session:
            await self._session.close()
        self._session = None

    @property
    def session(self) -> ClientSession:
        if not self._session:
            raise HttpError("Client is not initialized")
        return self._session

    async def get(
        self,
        url: str,
        *,
        headers: dict | None = None,
        params: dict | None = None,
    ) -> dict | list[dict]:
        return await self._request("GET", url, headers=headers, params=params)

    async def post(
        self,
        url: str,
        *,
        headers: dict | None = None,
        params: dict | None = None,
        json: dict | list | None = None,
        data: dict | list | str | bytes | None = None,
    ) -> dict | list[dict]:
        return await self._request(
            "POST", url, headers=headers, params=params, json=json, data=data
        )

    async def put(
        self,
        url: str,
        *,
        headers: dict | None = None,
        params: dict | None = None,
        json: dict | list | None = None,
        data: dict | list | str | bytes | None = None,
    ) -> dict | list[dict]:
        return await self._request(
            "PUT", url, headers=headers, params=params, json=json, data=data
        )

    async def delete(
        self,
        url: str,
        *,
        headers: dict | None = None,
        params: dict | None = None,
        json: dict | list | None = None,
        data: dict | list | str | bytes | None = None,
    ) -> dict | list[dict]:
        return await self._request(
            "DELETE", url, headers=headers, params=params, json=json, data=data
        )

    async def _request(
        self,
        method: str,
        url: str,
        *,
        headers: dict | None = None,
        params: dict | None = None,
        json: dict | list | None = None,
        data: dict | list | str | bytes | None = None,
    ) -> dict | list[dict]:
        try:
            async with self.session.request(
                method, url, headers=headers, params=params, json=json, data=data
            ) as response:
                if response.status == 200:
                    return await response.json()

                text = await response.text()
                raise HttpError(f"{method} {url} failed ({response.status}): {text}")

        except ClientConnectionError as e:
            raise HttpError(f"{method} {url} connection failed") from e

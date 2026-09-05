from typing import TypeVar

from aiohttp import ClientError, ClientSession, ClientTimeout

from .exceptions import HttpError

T = TypeVar("T", dict, list)


class HttpTransport:

    def __init__(self, timeout: float = 30.0):
        self._timeout = timeout
        self._session: ClientSession | None = None

    async def init(self) -> None:
        self._session = ClientSession(timeout=ClientTimeout(total=self._timeout))

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
        expected_type: type[T] = dict,
    ) -> T:
        return await self._request(
            "GET", url, headers=headers, params=params, expected_type=expected_type
        )

    async def post(
        self,
        url: str,
        *,
        headers: dict | None = None,
        params: dict | None = None,
        json: dict | list | None = None,
        data: dict | list | str | bytes | None = None,
        expected_type: type[T] = dict,
    ) -> T:
        return await self._request(
            "POST",
            url,
            headers=headers,
            params=params,
            json=json,
            data=data,
            expected_type=expected_type,
        )

    async def put(
        self,
        url: str,
        *,
        headers: dict | None = None,
        params: dict | None = None,
        json: dict | list | None = None,
        data: dict | list | str | bytes | None = None,
        expected_type: type[T] = dict,
    ) -> T:
        return await self._request(
            "PUT",
            url,
            headers=headers,
            params=params,
            json=json,
            data=data,
            expected_type=expected_type,
        )

    async def delete(
        self,
        url: str,
        *,
        headers: dict | None = None,
        params: dict | None = None,
        json: dict | list | None = None,
        data: dict | list | str | bytes | None = None,
        expected_type: type[T] = dict,
    ) -> T:
        return await self._request(
            "DELETE",
            url,
            headers=headers,
            params=params,
            json=json,
            data=data,
            expected_type=expected_type,
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
        expected_type: type[T] = dict,
    ) -> T:
        try:
            async with self.session.request(
                method, url, headers=headers, params=params, json=json, data=data
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise HttpError(f"{method} {url} failed ({response.status}): {text}")

                result = await response.json()
                if not isinstance(result, expected_type):
                    raise HttpError(
                        f"{method} {url}: expected {expected_type.__name__}, "
                        f"got {type(result).__name__}"
                    )
                return result

        except (ClientError, TimeoutError) as e:
            raise HttpError(f"{method} {url} request failed: {e}") from e

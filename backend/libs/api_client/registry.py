import asyncio

import httpx

from libs.config import settings

from .models import ApiRetrySettings, ApiTransportSettings

from .transport import AsyncRetryTransport


class HttpTransportRegistry:
    """Registry of api client connections"""

    _registry: dict[str, httpx.AsyncBaseTransport] = {}

    @classmethod
    def get(cls, url: str) -> httpx.AsyncBaseTransport | None:
        return cls._registry.get(url)

    @classmethod
    def put(cls, url: str, transport: httpx.AsyncBaseTransport) -> httpx.AsyncBaseTransport:
        cls._registry[url] = transport
        return transport

    @classmethod
    async def close_all(cls):
        jobs = [transport.aclose() for _, transport in cls._registry.items()]
        await asyncio.gather(*jobs)
        cls._registry.clear()

    @staticmethod
    def _get_settings() -> dict:
        return ApiTransportSettings(**settings.get("ASYNC_API_CLIENT", {})).dict(by_alias=True)

    @classmethod
    def create_default_transport(cls) -> httpx.AsyncBaseTransport:
        return httpx.AsyncHTTPTransport(**cls._get_settings())

    @classmethod
    def create_retriable_transport(cls, config: ApiRetrySettings) -> httpx.AsyncBaseTransport:
        return AsyncRetryTransport(config=config, **cls._get_settings())

    @classmethod
    def status(cls):
        return f'Persistent http transports: {list(cls._registry.keys())}'

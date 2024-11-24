from typing import Any, Iterable

from dynaconf.utils.boxing import DynaBox
from redis.asyncio import Redis


class CacheInterface:

    async def get(self, key: str, obj_type: Any = None):
        raise NotImplementedError

    async def mget(self, keys: Iterable[str], obj_type: Any = None) -> dict[str, Any]:
        raise NotImplementedError

    async def set(self, key: str, data: Any) -> None:
        raise NotImplementedError

    async def mset(self, content: dict[str, Any]) -> None:
        raise NotImplementedError


class RedisStorageInterface(CacheInterface):

    @classmethod
    def client(cls) -> Redis:
        raise NotImplementedError

    @classmethod
    def fabric_settings(cls) -> DynaBox:
        raise NotImplementedError

    @property
    def client_settings(self) -> DynaBox:
        raise NotImplementedError

    async def async_init(self):
        raise NotImplementedError

    async def is_available(self) -> bool:
        raise NotImplementedError

    async def ping(self) -> bool:
        raise NotImplementedError

    async def close(self):
        raise NotImplementedError

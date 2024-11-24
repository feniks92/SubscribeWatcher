import asyncio

from libs import logging
from libs.cache.client import RedisCache

log = logging.getLogger('cache')


class Cache:
    cache_client: RedisCache

    @property
    def cache_key(self):
        raise NotImplementedError

    @classmethod
    def cache(cls, func):
        async def _cache(self_, *args, **kwargs):
            data = await cls.cache_client.get(key=self_.cache_key)
            if data:
                log_message = f'{func.__name__.upper()} func result retrieved from cache'
                log.info(log_message)
                log.debug(log_message, extra={'data': data})
                return data

            data = await func(self_, *args, **kwargs)
            if data:
                asyncio.create_task(cls.cache_client.set(self_.cache_key, data))

            return data

        return _cache

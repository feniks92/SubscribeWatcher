import asyncio
import json
from datetime import timedelta
from typing import Any, Iterable, Optional, Union

from dynaconf.utils.boxing import DynaBox
from redis import asyncio as aioredis
from redis.asyncio.cluster import RedisCluster
from redis.asyncio.sentinel import Sentinel as RedisSentinel

from libs import logging
from libs.config import settings
from libs.utils.time import timedelta_from_duration

from .interface import CacheInterface, RedisStorageInterface
from .prometheus import CachePrometheusMixin
from .serializers import (DefaultSerializer, EncryptableSerializer,
                          HashableSerializer, RedisRecordSerializer)

logger = logging.getLogger('redis')


class DictCache(CacheInterface):

    def __init__(self):
        self.data: dict = {}

    @property
    def size(self):
        return len(self.data)

    async def get(self, key: str, obj_type: Any = None):
        return self.data.get(key)

    async def mget(self, keys: Iterable[str], obj_type: Any = None) -> dict[str, Any]:
        return {key: value for key, value in self.data.items() if key in keys}

    async def set(self, key: str, data: Any) -> None:
        self.data[key] = data

    async def mset(self, content: dict[str, Any]) -> None:
        self.data.update(content)

    async def clear(self):
        self.data.clear()


class RedisCache(RedisStorageInterface, CachePrometheusMixin):
    client: aioredis.Redis = None
    ping_timeout = 1
    fabric_settings: DynaBox = None

    encrypt_keys: bool = True,
    encrypt_data: bool = True,
    expire: Optional[Union[int, timedelta]] = None

    key_serializer = DefaultSerializer()
    value_serializer = DefaultSerializer()

    is_transaction: bool = False

    def __init__(self, is_transaction: bool = False):
        self._serializer = RedisRecordSerializer(
            key_serializer=(HashableSerializer(self.key_serializer)
                            if self.encrypt_keys else self.key_serializer),
            value_serializer=(EncryptableSerializer(self.value_serializer)
                              if self.encrypt_data else self.value_serializer),
        )
        self.is_transaction = is_transaction
        if self.is_transaction:
            self.client = self.client.pipeline()

    @classmethod
    def __fabric(cls):
        if not cls.fabric_settings:
            cls.fabric_settings = settings.CACHE
        return RedisClientFabric(config=cls.fabric_settings)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.execute()

    @classmethod
    async def async_init(cls):
        """ Call it once at startup hook """
        if cls.client:
            logger.warning("Don't run RedisCache:async_init function twice")

        instance = cls()
        cls.client = cls.client or await cls.__fabric().create_client(
            client_settings=RedisClientSettings.from_settings(config=cls.client_settings)
        )
        await cls.client.initialize()
        return instance

    @property
    def client_settings(self) -> DynaBox:
        raise NotImplementedError

    @property
    def _redis_connection_settings(self):
        if self.client:
            redis_settings = self.client.connection_pool.connection_kwargs
            return redis_settings

    async def exists(self, key: str) -> bool:
        key_ = self._serializer.encode_key(key)
        return bool(await self.client.exists(key_))

    async def keys(self, pattern: str) -> list[str]:
        try:
            async with self.measure('keys'):
                return await self.client.keys(pattern)
        except Exception:
            logger.exception('Error trying get value from redis')
            return []

    async def get(self, key: str, obj_type: Any = None) -> Any:
        # TODO: Remove obj_type argument
        if not key:
            return None

        key_ = self._serializer.encode_key(key)
        try:
            async with self.measure('get'):
                out = await self.client.get(key_)
                self._hit = bool(out)
                self._miss = not self._hit
            return self._serializer.decode(out)
        except Exception:
            logger.exception('Error trying get value from redis')
            return None

    async def mget(self, keys: Iterable[str], obj_type: Any = None) -> dict[str, Any]:
        if not keys:
            return {}

        keys_ = [self._serializer.encode_key(key) for key in keys]
        try:
            async with self.measure('mget'):
                results = await self.client.mget(keys_)
                self._hit = bool(results)
                self._miss = not self._hit
            return dict(zip(keys, [self._serializer.decode(out) for out in results]))
        except Exception:
            logger.exception('Error trying mget value from redis')
            return {}

    async def hget(self, name: str, key: str) -> Any:
        if not key:
            return None

        key_ = self._serializer.encode_key(key)
        try:
            async with self.measure('hget'):
                out = await self.client.hget(name, key_)
                self._hit = bool(out)
                self._miss = not self._hit
            return self._serializer.decode(out)
        except Exception:
            logger.exception('Error trying get value from redis')
            return None

    async def hgetall(self, name: str) -> dict[str, Any]:
        if not name:
            return {}

        key_ = self._serializer.encode_key(name)
        try:
            async with self.measure('hgetall'):
                out = await self.client.hgetall(key_)
                self._hit = bool(out)
                self._miss = not self._hit
            return {k: self._serializer.decode(v) for k, v in out.items()}
        except Exception:
            logger.exception('Error trying get value from redis')
            return {}

    async def hmget(self, name: str, keys: Iterable[str]) -> dict[str, Any]:
        if not keys:
            return {}

        keys_ = [self._serializer.encode_key(key) for key in keys]
        try:
            async with self.measure('hmget'):
                results = await self.client.hmget(name, keys_)
                self._hit = bool(results)
                self._miss = not self._hit
            return dict(zip(keys, [self._serializer.decode(out) for out in results]))
        except Exception:
            logger.exception('Error trying mget value from redis')
            return {}

    @staticmethod
    def masked_key(key: str):
        return f'{"*" * (len(key) - 3)}{key[-3:]}'

    async def set(self, key: str, data: Any) -> None:
        key_, value_ = self._serializer.encode(key, data)
        if value_:
            try:
                async with self.measure('set'):
                    await self.client.set(key_, value_, px=self.expire)

                logger.info(f'{data.__class__.__name__!r} set to cache with key {self.masked_key(key)}')
            except Exception:
                logger.exception('Error setting value to redis')

    async def mset(self, content: dict[str, Any]) -> None:
        try:
            async with self.measure('mset'):
                content_ = dict([self._serializer.encode(key, value) for key, value in content.items()])
                await self.client.mset(content_)
        except Exception:
            logger.exception('Error setting value to redis')

    async def hset(self, name: str, key: str, data: Any) -> None:
        key_, value_ = self._serializer.encode(key, data)
        if value_:
            try:
                async with self.measure('hset'):
                    await self.client.hset(name, key=key_, value=value_)
                logger.info(f'{type(data)} set to cache with key {self.masked_key(key)}')
            except Exception:
                logger.exception('Error setting value to redis')

    async def hmset(self, name: str, content: dict[str, Any]) -> None:
        try:
            async with self.measure('hmset'):
                content_ = dict([self._serializer.encode(key, value) for key, value in content.items()])
                await self.client.hmset(name, content_)
        except Exception:
            logger.exception('Error setting value to redis')

    async def hdel(self, name: str, keys: Iterable[str] | None = None):
        try:
            async with self.measure('hdel'):
                if keys:
                    await self.client.hdel(name, *keys)
                else:
                    await self.client.hdel(name)
        except Exception:
            logger.exception('Error deleting value from redis')

    async def delete(self, name: str, keys: Iterable[str] | None = None):
        try:
            async with self.measure('delete'):
                if keys:
                    await self.client.delete(*keys)
                else:
                    await self.client.delete(name)
        except Exception:
            logger.exception('Error deleting value from redis')

    @classmethod
    async def is_available(cls) -> bool:
        if not cls.client:
            return False
        try:
            return await asyncio.wait_for(cls.ping(), timeout=cls.ping_timeout)
        except (ConnectionError, aioredis.exceptions.ConnectionError):
            logger.exception('Redis connection error', extra={'connection_string': cls._redis_connection_settings})
            return False
        except (aioredis.exceptions.TimeoutError, asyncio.TimeoutError):
            logger.exception('Redis connection timeout', extra={'connection_string': cls._redis_connection_settings})
            return False

    @classmethod
    async def ping(cls) -> bool:
        return await cls.client.ping()

    @classmethod
    async def close(cls):
        await cls.client.close()
        logger.debug(f'Redis client {cls._redis_connection_settings} closed.')

    async def flushdb(self):
        await self.client.flushdb(asynchronous=True)
        logger.debug('Redis db flushed.')

    async def execute(self):
        if self.is_transaction:
            await self.client.execute()
            logger.debug('Pipeline records commited.')


class RedisClientSettings:
    def __init__(self,
                 url,
                 password,
                 is_cluster=None,
                 is_sentinel=None,
                 sentinels=None,
                 sentinels_group_name=None,
                 db=0):
        self.url = url
        self.password = password
        self.is_cluster = is_cluster
        self._is_sentinel = is_sentinel
        self.sentinels = self._parse_sentinels(sentinels=sentinels)
        self.sentinels_group_name = sentinels_group_name
        self.db = db

    @property
    def is_sentinel(self):
        return self._is_sentinel and self.sentinels and self.sentinels_group_name

    @classmethod
    def from_settings(cls, config: DynaBox):
        return cls(url=config.URL,
                   password=config.PASSWORD,
                   is_cluster=config.IS_CLUSTER,
                   is_sentinel=config.IS_SENTINEL,
                   sentinels=config.SENTINELS,
                   sentinels_group_name=config.SENTINELS_MASTER_GROUP_NAME,
                   db=config.get('DB', 0))

    @staticmethod
    def _parse_sentinels(sentinels: str):
        """ Парсит JSON REDIS SENTINEL settings в подходящий формат для параметра sentinels класса RedisSentinel

        Example: '["host:port", "host:port"]'
        """
        if not sentinels:
            return

        _sentinels = []
        try:
            _sentinels = json.loads(sentinels)
            _sentinels = [sentinel.split(':') for sentinel in _sentinels]
        except json.JSONDecodeError as exc:
            logger.error(f'Неверный формат настройки conf.SENTINELS, должен быть JSON. ({exc})')

        return _sentinels


class RedisClientFabric:
    def __init__(self, config):
        self.connection_pool_enable = config.CONNECTION_POOL_ENABLE
        self.default_options = dict(max_connections=config.MAX_POOL_CONNECTIONS,
                                    timeout=config.MAX_POOL_CONNECTIONS_TIMEOUT,
                                    socket_connect_timeout=config.SOCKET_CONNECT_TIMEOUT,
                                    encoding="utf-8",
                                    decode_responses=True)

    async def create_client(self, client_settings: RedisClientSettings, **options):
        _client_type = ''
        _conn_type = 'POOL'
        _options = dict(**self.default_options, **options)
        if client_settings.is_sentinel:
            redis = await self.create_sentinel_client(client_settings, **_options)
            _client_type = 'with SENTINELS'
        elif client_settings.is_cluster:
            options['socket_timeout'] = _options.pop('timeout', None)
            redis = self.create_cluster_client(client_settings, **_options)
            _conn_type = 'CLUSTER'
        else:
            redis = self.create_default_client(client_settings, **_options)

        if not self.connection_pool_enable:
            _conn_type = 'SINGLE'  # Redis client bound to single connection (no auto reconnection).
            redis = redis.client()

        logger.debug('REDIS connection settings:', extra={'url': {'full': client_settings.url},
                                                          'options': _options,
                                                          'client_type': _client_type,
                                                          'conn_type': _conn_type,
                                                          })
        return redis

    @staticmethod
    def get_connection_pool(client: RedisClientSettings, **options):
        return aioredis.BlockingConnectionPool.from_url(url=client.url,
                                                        password=client.password,
                                                        **options)

    async def create_sentinel_client(self, client: RedisClientSettings, **options):
        options['db'] = client.db
        sentinel_redis = RedisSentinel(sentinels=client.sentinels,
                                       sentinel_kwargs=dict(password=client.password),
                                       connection_pool=self.get_connection_pool(client, **options),
                                       password=client.password)
        return await sentinel_redis.master_for(service_name=client.sentinels_group_name)

    @staticmethod
    def create_cluster_client(client: RedisClientSettings, **options):
        return RedisCluster.from_url(url=client.url,
                                     password=client.password,
                                     **options)

    def create_default_client(self, client: RedisClientSettings, **options):
        return aioredis.Redis(connection_pool=self.get_connection_pool(client, **options),
                              password=client.password)


class BaseCommonCache(RedisCache):
    client_settings = settings.CACHE.COMMON

    encrypt_keys: bool = settings.CACHE.COMMON.USE_ENCRYPTION.KEY,
    encrypt_data: bool = settings.CACHE.COMMON.USE_ENCRYPTION.VALUE,
    expire: Optional[Union[int, timedelta]] = timedelta_from_duration(settings.CACHE.COMMON.TTL)
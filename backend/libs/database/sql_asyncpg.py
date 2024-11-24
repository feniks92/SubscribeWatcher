import asyncpg
from sqlalchemy import Visitable

from libs import logging

log = logging.getLogger('sql_asyncpg')


class AdapterConnection(asyncpg.Connection):
    """ Предназначен для преобразования запросов Alchemy в RAW sql запросы

    TODO на данный момент частично сработало, т.к. в datasources идет дальнейшая обработка результата как alchemy
    TODO т.е. требуется во всех datasource поправить обработку результата полученного из connection
    """

    async def execute(self, query, *args, **kwargs):
        if isinstance(type(query), Visitable):
            query_ = query.compile(compile_kwargs={"literal_binds": True}).__str__()
            return await super().execute(query_, *args, **kwargs)
        return await super().execute(query, *args, **kwargs)


class AsyncPgConnection:

    def __init__(self, url: str, timeout: int = 1, cache_result: bool = False):
        self.dsn = url
        self.timeout = timeout
        self.cache_result = cache_result
        self.connection = None
        self.connection_class = AdapterConnection

    async def __call__(self, *args, **kwargs):
        return await self._create_connection()

    async def _create_connection(self):
        db_settings = {
            'dsn': self.dsn,
            'timeout': self.timeout
        }
        if self.cache_result:
            self.connection = await asyncpg.connect(**db_settings,
                                                    connection_class=self.connection_class)
        self.connection = await asyncpg.connect(**db_settings,
                                                connection_class=self.connection_class,
                                                statement_cache_size=0)
        return self.connection

    async def _close_connection(self):
        if self.is_connected():
            await self.connection.close()
            self.connection = None

    async def __aenter__(self):
        return await self._create_connection()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_connection()

    def is_connected(self) -> bool:
        return self.connection and not self.connection.is_closed()

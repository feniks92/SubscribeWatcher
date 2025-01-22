import asyncio
from abc import ABC, abstractmethod
from http import HTTPStatus

from httpx import AsyncClient
from libs import logging
from starlette.requests import Request

from .registry import HealthCheckCollector

sqlalchemy = None
try:
    import sqlalchemy
except ImportError:
    pass

log = logging.getLogger('health')


class HTTPStatusCheck(HealthCheckCollector):
    service_name: str
    url: str
    expected_status_code: int = HTTPStatus.OK
    verify_certificate: bool = True
    follow_redirects: bool = False

    @property
    def help_text(self):
        return f'Check wheather {self.service_name} is accessible'

    async def _run(self, request: Request) -> bool:
        async with AsyncClient(verify=self.verify_certificate) as client:
            try:
                response = await client.get(self.url, follow_redirects=self.follow_redirects)
            except Exception:
                log.exception(f"{self.service_name} healthcheck exception")
                return False
            else:
                log.debug(f"{self.service_name} healthcheck response", extra={'status_code': response.status_code})
                if response.status_code == self.expected_status_code:
                    return True

                log.info(f"{self.service_name} healthcheck failed", extra={'status_code': response.status_code})
                return False


class PostgreSQLCheck(HealthCheckCollector):
    metric_name = 'postgresql_state'
    help_text = 'Check wheather internal PostgreSQL cluster is accessible'
    internal = True

    async def _get_db_session(self):
        session = self.get_db_session()
        if asyncio.iscoroutine(session):
            return await session
        return session

    def get_db_session(self):
        """
        Implement this method for particular application
        """
        raise NotImplementedError

    async def _run(self, request: Request) -> bool:
        session = await self._get_db_session()
        try:
            query = 'SELECT 1'
            if sqlalchemy:
                query = sqlalchemy.text(query)
            await session.execute(query)
        except Exception:  # noqa
            log.exception("PostgreSQL healthcheck failed")
            return False
        else:
            return True
        finally:
            await session.close()


class PingCheck(HealthCheckCollector, ABC):

    def __init__(self):
        super(PingCheck, self).__init__()
        if not self.__has_method('ping'):
            raise AssertionError(f'Client {self._client_name} must implement "ping" method.')  # nosec

    def __has_method(self, name):
        return callable(getattr(self.client, name, None))

    @property
    @abstractmethod
    def service_name(self):
        pass

    @property
    @abstractmethod
    def client(self):
        pass

    @property
    def _client_name(self):
        return self.client.__name__

    @property
    def name(self):
        return self.service_name or self._client_name

    @property
    def metric_name(self):
        return f'{self.name}_state'

    @property
    def help_text(self):
        return f'Ping {self.name} service is accessible'

    async def _run(self, request: Request) -> bool:
        try:
            result = await self.client.ping()
            log.debug(f"{self.name} ping healthcheck {result=}")
            return result
        except Exception:
            log.exception(f"{self.name} healthcheck exception")
            return False

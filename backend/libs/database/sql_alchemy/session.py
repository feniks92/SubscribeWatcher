from contextvars import ContextVar
from functools import wraps
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, sessionmaker

from libs import logging

from .async_session import AsyncSessionWithMetrics
from .connector import SQLAlchemyConnector
from .exceptions import MissingSessionError, SessionNotInitialisedError

log = logging.getLogger('sql_alchemy')

SessContextVar = ContextVar[Optional[Session]]

_ac_session_ctx: SessContextVar = ContextVar('_db_session', default=None)
_trans_session_ctx: SessContextVar = ContextVar('_db_trans_session', default=None)


class DBSessionBase:
    _connector = None
    _sessionmaker: sessionmaker = None
    _session_ctx: SessContextVar = None

    def __init__(self):
        self._session = None
        self._session_token = None

    @property
    def engine(self):
        return self._connector.engine

    @property
    def session(self) -> Session:
        """Return an instance of Session local to the current async context."""
        if self._session is None:
            raise MissingSessionError

        return self._session

    def _new_session(self) -> Session:
        if not isinstance(self._sessionmaker, sessionmaker):
            raise SessionNotInitialisedError
        return self._sessionmaker()

    async def __aenter__(self):
        self._session = self._new_session()
        self._session_token = self._session_ctx.set(self._session)
        return self._session

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._session.close()
        self._session_ctx.reset(self._session_token)


class DBSessionMeta(type):
    _connector: SQLAlchemyConnector = None
    _sessionmaker: sessionmaker = None

    def __call__(cls, *args, **kwargs):
        cls._connector = cls._connector or SQLAlchemyConnector.create(isolation_level=cls.isolation_level)
        cls._sessionmaker = cls._sessionmaker or sessionmaker(autoflush=False,
                                                              future=True,
                                                              bind=cls._connector.engine,
                                                              class_=AsyncSessionWithMetrics)
        return super().__call__(*args, **kwargs)


class DBAutocommitSession(DBSessionBase, metaclass=DBSessionMeta):
    isolation_level = 'AUTOCOMMIT'
    _session_ctx = _ac_session_ctx


class DBTransactionalSession(DBSessionBase, metaclass=DBSessionMeta):
    isolation_level = 'READ COMMITTED'
    _session_ctx = _trans_session_ctx


async def pass_db_session() -> AsyncSession:
    async with DBAutocommitSession() as sess:
        yield sess


async def pass_transactional_session() -> AsyncSession:
    async with DBTransactionalSession() as sess:
        yield sess


def db_bound(route):
    """
    Simple wrapper for db-bound route handlers, ensures session creation and closure for each request.
    """

    @wraps(route)
    async def wrapper(*args, **kwargs):
        async with DBAutocommitSession():
            return await route(*args, **kwargs)

    return wrapper


def get_db_session() -> Session:
    try:
        return _ac_session_ctx.get()
    except MissingSessionError:
        return _trans_session_ctx.get()
    except Exception:
        raise

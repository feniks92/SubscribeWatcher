from enum import StrEnum

from libs.database.config import asyncpg_settings
from libs.database.setting_models import AsyncPgSettings
from libs.database.sql_alchemy.session import DBAutocommitSession  # noqa
from libs.database.sql_alchemy.session import (DBTransactionalSession,
                                               pass_db_session,
                                               pass_transactional_session)
from libs.database.sql_asyncpg import AsyncPgConnection


class DbEngineType(StrEnum):
    alchemy = 'alchemy'
    asyncpg = 'asyncpg'


class DbIsolationLevelType(StrEnum):
    autocommit = 'autocommit'
    transaction = 'transaction'


def get_session_by_engine(type_engine: DbEngineType = DbEngineType.alchemy,
                          isolation_level: DbIsolationLevelType = DbIsolationLevelType.autocommit):
    match type_engine:
        case DbEngineType.alchemy:
            match isolation_level:
                case DbIsolationLevelType.transaction:
                    return pass_transactional_session
                case DbIsolationLevelType.autocommit:
                    return pass_db_session

        case DbEngineType.asyncpg:
            return pass_asyncpg_connection


def get_asyncpg_connection(settings: AsyncPgSettings = asyncpg_settings):
    return AsyncPgConnection(url=settings.URL,
                             timeout=settings.TIMEOUT,
                             cache_result=settings.CACHE_RESULT)


async def pass_asyncpg_connection():
    async with get_asyncpg_connection() as conn:
        yield conn

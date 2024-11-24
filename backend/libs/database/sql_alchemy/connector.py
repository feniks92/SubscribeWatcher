import json
import time

from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import Engine
from sqlalchemy.pool import NullPool

from libs import metrics
from libs.database.config import sqlalchemy_settings

METRIC_PREFIX = 'sql_queries'


class SQLAlchemyConnector:
    metrics_prefix = METRIC_PREFIX

    def __init__(self, engine):
        self._engine = engine

    @property
    def engine(self):
        return self._engine

    @metrics.metric
    def total(self):
        return metrics.Counter('Number of complete SQL queries', labelnames=('type',))

    @metrics.metric
    def in_progress(self):
        return metrics.Gauge('Number of SQL queries in progress')

    @metrics.metric
    def duration_seconds(self):
        return metrics.Histogram('SQL query duration, in seconds')

    def _before_cursor_execute_hook(self, conn, *_):
        conn.info.setdefault('query_start_time', []).append(time.perf_counter())
        if sqlalchemy_settings.COLLECT_METRICS:
            self.in_progress.inc()

    def _after_cursor_execute_hook(self, conn, *_):
        if sqlalchemy_settings.COLLECT_METRICS:
            self.in_progress.dec()
            self.duration_seconds.observe(time.perf_counter() - conn.info['query_start_time'].pop(-1))

    def _after_execute_hook(self, _conn, statement, *_):
        if sqlalchemy_settings.COLLECT_METRICS:
            self.total.labels(get_statement_type(statement)).inc()

    @staticmethod
    def _do_connect_hook(dialect, _, cargs, cparams):
        """
        SqlAlchemy and asyncpg require different format for multi-host database connection strings:
        SqlAlchemy: PROTOCOL+asyncpg://USER:PASSWORD@/DATABASE?host=HOST_PORT_1&host=HOST_PORT_2
        asyncpg: PROTOCOL://USER:PASSWORD@HOST_PORT_1,HOST_PORT_2/DATABASE
                 or PROTOCOL://USER:PASSWORD@HOST_1,HOST_2:PORT_1,PORT_2/DATABASE

        Also asyncpg does not support a sequence of hosts as an argument to its internal 'connect' function
        (but SqlAlchemy passes tuple).
        When this is fixed, listener could be removed.

        To make format compatible, we recreade asyncpg-compatible DSN from existing parsed SqlAlchemy connection
        parameters.
        """
        host = cparams['host']
        if not isinstance(host, (tuple, list)):
            return

        host = ','.join(host)

        custom_params = {k: v for k, v in cparams.items() if k not in ['host', 'user', 'password', 'database']}
        custom_params['dsn'] = 'postgresql://{user}:{password}@{host}/{database}'.format(
            user=cparams.get('user', ''),
            password=cparams.get('password', ''),
            host=host,
            database=cparams.get('database', ''),
        )
        return dialect.connect(*cargs, **custom_params)

    @classmethod
    def create(cls, isolation_level: str = 'AUTOCOMMIT'):
        engine_kwargs = dict(pool_pre_ping=True,
                             echo=sqlalchemy_settings.ECHO,
                             isolation_level=isolation_level,
                             pool_reset_on_return=True,
                             echo_pool=sqlalchemy_settings.POOL_LOG,
                             connect_args={'timeout': sqlalchemy_settings.CONNECT_TIMEOUT},
                             json_serializer=lambda obj: json.dumps(obj, default=str))
        if sqlalchemy_settings.NO_POOLING:
            engine_kwargs['poolclass'] = NullPool
        else:
            engine_kwargs.update(dict(
                pool_size=sqlalchemy_settings.POOL_SIZE,
                max_overflow=sqlalchemy_settings.POOL_MAX_OVERFLOW))
        engine = create_async_engine(sqlalchemy_settings.URL, **engine_kwargs)

        connector = cls(engine)
        if not getattr(cls, '_hooks_bound', False):  # prevent repetitive listener registration
            event.listen(Engine, 'do_connect', connector._do_connect_hook)
            event.listen(Engine, 'before_cursor_execute', connector._before_cursor_execute_hook)
            event.listen(Engine, 'after_cursor_execute', connector._after_cursor_execute_hook)
            event.listen(Engine, 'after_execute', connector._after_execute_hook)
            cls._hooks_bound = True
        return connector


def get_statement_type(statement) -> str:
    if statement.is_delete:
        return 'delete'
    elif statement.is_insert:
        return 'insert'
    elif statement.is_update:
        return 'update'
    elif statement.is_select:
        return 'select'
    return 'other'

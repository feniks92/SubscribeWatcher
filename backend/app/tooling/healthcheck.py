from libs import logging
from libs.cache.client import BaseCommonCache
from libs.cache.healthcheck import RedisCheck
from libs.database.sql_alchemy import get_db_session
from libs.health import HealthRegistry
from libs.health.checks import PostgreSQLCheck

log = logging.getLogger('health')


class DBCheck(PostgreSQLCheck):
    def get_db_session(self):
        return get_db_session()


class CacheCommonCheck(RedisCheck):
    metric_name = 'cache_appeals_state'
    help_text = 'Check Redis cache for Appeals service is accessible'
    client = BaseCommonCache


health_registry = HealthRegistry(
    DBCheck(),
    CacheCommonCheck(),
    app_name='Subscribe Watcher Service'
)

from libs import logging
from libs.health.checks import PingCheck

from .client import RedisCache

log = logging.getLogger('health')


class RedisCheck(PingCheck):
    service_name = 'redis'
    client: RedisCache

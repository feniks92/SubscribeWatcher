from contextlib import asynccontextmanager
from typing import ClassVar, Optional

from libs import metrics


class CachePrometheusMixin(metrics.BasePrometheusMixin):
    metrics_prefix: ClassVar[str] = 'UNDEFINED'
    service_name: ClassVar[str] = 'UNDEFINED'
    buckets: ClassVar[Optional[list[float]]] = metrics.DEFAULT_BUCKETS
    _miss: bool = False
    _hit: bool = False

    @metrics.metric
    def cache_hit_count(self):
        return metrics.Counter(
            f'Count of hits to cache {self.service_name or self.metrics_prefix}'
        )

    @metrics.metric
    def cache_miss_count(self):
        return metrics.Counter(
            f'Count of hits to cache {self.service_name or self.metrics_prefix}'
        )

    @asynccontextmanager
    async def measure(self, action):
        try:
            async with super(CachePrometheusMixin, self).measure(action):
                yield
        finally:
            if self._hit:
                self.cache_hit_count.inc()
            if self._miss:
                self.cache_miss_count.inc()

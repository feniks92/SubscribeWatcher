from sqlalchemy.ext.asyncio import AsyncSession

from libs import metrics

METRIC_PREFIX = 'sql_queries'
DEFAULT_ISOLATION_LEVEL = 'READ COMMITTED'


class AsyncSessionWithMetrics(AsyncSession):
    metrics_prefix = METRIC_PREFIX
    isolation_level = DEFAULT_ISOLATION_LEVEL

    @metrics.metric
    def errors_count(self):
        return metrics.Counter('Database request errors', labelnames=('type',))

    async def execute(self, *args, **kwargs):
        try:
            return await super().execute(*args, **kwargs)
        except Exception as err:
            self.errors_count.labels(str(err.__class__.__name__)).inc()
            raise

    def begin(self, **kw):
        self.isolation_level = kw.pop('isolation_level', DEFAULT_ISOLATION_LEVEL)
        return super().begin(**kw)

    def begin_autocommit(self):
        return self.begin(isolation_level='AUTOCOMMIT')

    async def __aenter__(self):
        await self.connection(execution_options={'isolation_level': self.isolation_level})
        return await super().__aenter__()

    def _regenerate_proxy_for_target(self, target):
        raise NotImplementedError()

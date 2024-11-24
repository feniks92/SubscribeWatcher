import asyncio
from typing import Iterable

from prometheus_client import CollectorRegistry, Metric
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector
from shared import logging
from shared.config import settings
from starlette.requests import Request

log = logging.getLogger('health')


class HealthMetric(GaugeMetricFamily):
    """
    Passes collector's "internal" property to registry on rendering
    """
    app_label_name = 'app_name'

    def __init__(self, *args, internal=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.internal = internal

    @classmethod
    def with_app_label(cls, name: str, help_text: str, value: float, internal: bool = True):
        metric = cls(name, help_text, labels=(cls.app_label_name,), internal=internal)
        metric.add_metric(labels=(settings.SERVICE.APP_NAME,), value=value)
        return metric

    def _check_global_status(self) -> bool:
        if not self.internal:
            return True

        if not self.samples:
            return False

        return all(bool(s.value) for s in self.samples)


class HealthCheckCollector:
    """
    Custom collector for health checks, must be run() before metrics collection.
    """
    metric_name: str
    help_text: str = ''
    active: bool = True
    internal: bool = False  # internal services are required to be healthy for reporting entire service is healthy

    def __init__(self):
        self._healthy = False

    def collect(self):
        yield HealthMetric.with_app_label(self.metric_name, self.help_text,
                                          value=int(self._healthy),
                                          internal=self.internal)

    async def run(self, request: Request) -> None:
        """
        Don't update self._health until a specific value received.
        Otherwise, the collect() may receive an incorrect value,
        because prometheus library calls collect() on different threads
        """
        try:
            self._healthy = await self._run(request)
        except BaseException:  # noqa
            self._healthy = False
            log.exception("Unexpected healthcheck exception", extra={'healthcheck': self.__class__.__name__})

    async def _run(self, request: Request) -> bool:
        raise NotImplementedError


class HealthRegistry(CollectorRegistry):
    healthchecks: list[HealthCheckCollector] = []

    def __init__(self, *healthchecks: HealthCheckCollector, app_name: str = 'service'):
        super().__init__()
        self.app_name = app_name
        for check in healthchecks:
            if check.active:
                self.register(check)

    def collect(self) -> Iterable[Metric]:
        """
        Yield metrics from the collectors in the registry, then compute and yield cumulative service state metric.
        """
        service_healthy = 1
        for metric in super().collect():
            yield metric
            if not metric._check_global_status():  # noqa
                service_healthy = 0

        yield HealthMetric.with_app_label('state',
                                          f'Cumulative {self.app_name} state',
                                          value=service_healthy)

    def register(self, collector: Collector):
        self.healthchecks.append(collector)
        super().register(collector)

    async def run(self, request: Request):
        await asyncio.gather(*[check.run(request) for check in self.healthchecks])

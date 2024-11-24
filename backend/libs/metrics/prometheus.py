import time
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import ClassVar, Optional

from httpx import Request

from .metric import Counter, Gauge, Histogram, metric

DEFAULT_BUCKETS = [0.1, 0.25, 0.5, 0.75, 1.0, 2.0]


class BasePrometheusMiddleware:
    """
    Each ApiClient should have separate subclass of BasePrometheusMiddleware
    and add its instance in __init__ method - to prevent mixing of metrics

    Inspired by starlette prometheus exporter:
    https://github.com/stephenhillier/starlette_exporter/blob/master/starlette_exporter/middleware.py
    """

    metrics_prefix: ClassVar[str] = ''
    service_name: ClassVar[str] = ''
    buckets: ClassVar[Optional[list[float]]] = DEFAULT_BUCKETS
    extra_labels: Optional[dict] = None

    @metric
    def requests_total(self):
        return Counter(
            f"Total HTTP requests to {self.service_name or self.metrics_prefix}",
            labelnames=('method', 'path', 'status_code', *self._extra_labels.keys()),
        )

    @metric
    def request_duration_seconds(self):
        return Histogram(
            "HTTP request duration, in seconds",
            labelnames=("method", "path", "status_code", *self._extra_labels.keys()),
            buckets=self.buckets,
        )

    @metric
    def requests_in_progress(self):
        return Gauge(
            f"Total HTTP requests to {self.service_name or self.metrics_prefix} currently in progress",
            labelnames=('method', *self._extra_labels.keys()),
            multiprocess_mode='livesum',
        )

    def __init__(self, extra_labels=None):
        self._extra_labels = extra_labels or self.extra_labels or {}

    def _before_call(self, request: Request, **request_kwargs) -> tuple[float, dict, dict]:
        in_progress_labels = {'method': request.method, **self._extra_labels}
        self.requests_in_progress.labels(**in_progress_labels).inc()

        path = request_kwargs['url']
        labels = {'path': path, 'status_code': 'unknown', **in_progress_labels}
        start = time.perf_counter()

        return start, in_progress_labels, labels

    def _after_call(self, start: float, in_progress_labels: dict, labels: dict) -> None:
        end = time.perf_counter()
        self.requests_in_progress.labels(**in_progress_labels).dec()
        self.requests_total.labels(**labels).inc()
        self.request_duration_seconds.labels(**labels).observe(end - start)


class BasePrometheusMixin(ABC):
    buckets: ClassVar[Optional[list[float]]] = DEFAULT_BUCKETS

    @property
    @abstractmethod
    def metrics_prefix(self):
        pass

    @property
    @abstractmethod
    def service_name(self):
        pass

    @metric
    def request_duration_seconds(self):
        return Histogram(
            "Cache handling duration, in seconds",
            labelnames=('status', 'action'),
            buckets=self.buckets,
        )

    @metric
    def requests_total(self):
        return Counter(
            f'Total count of handling {self.service_name or self.metrics_prefix}',
            labelnames=('status', 'action')
        )

    @asynccontextmanager
    async def measure(self, action):
        begin = time.monotonic()
        status = 'ok'
        try:
            yield
        except Exception as e:
            status = 'error'
            raise e
        finally:
            end = time.monotonic()
            labels = (status, action)
            self.requests_total.labels(*labels).inc()
            self.request_duration_seconds.labels(*labels).observe(end - begin)

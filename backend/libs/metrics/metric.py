import time
from functools import cached_property, wraps
from typing import Any, Callable, Optional, Self, Type

import prometheus_client.metrics as prometheus

from libs.config import APP_CONFIG

MetricType = Type[prometheus.MetricWrapperBase]

_metrics: dict[str, MetricType] = {}

DEFAULT_BUCKETS = [0.1, 0.25, 0.5, 0.75, 1.0, 2.0]


class AppLabelMixin:
    """
    Forces metric collector to use 'app_name' label with settings-defined value
    """
    app_name_label = 'app_name'

    def __init__(self, *args, **kwargs):
        labelnames = kwargs.get('labelnames', ())

        if self.app_name_label not in labelnames:
            if not labelnames:  # define label value for metrics having no custom labels
                kwargs['_labelvalues'] = [self.app_name]

            kwargs['labelnames'] = tuple([self.app_name_label, *labelnames])

        super().__init__(*args, **kwargs)

    @cached_property
    def app_name(cls):
        return APP_CONFIG.APP_NAME

    def labels(self, *labelvalues: Any, **labelkwargs: Any):
        """
        Add app_name label to label set
        """
        if labelvalues:
            labelvalues = [self.app_name, *labelvalues]
        elif labelkwargs:
            labelkwargs[self.app_name_label] = self.app_name
        return super().labels(*labelvalues, **labelkwargs)


def lazy_metric(cls):
    _cls = type(f'Lazy{cls.__name__}', (AppLabelMixin, cls), {})

    def lazy_wrapper(documentation, **kwargs):
        @wraps(_cls)
        def lazy_init(name: str):
            return _cls(name=name, documentation=documentation, **kwargs)

        return lazy_init

    return lazy_wrapper


Counter = lazy_metric(prometheus.Counter)
Gauge = lazy_metric(prometheus.Gauge)
Histogram = lazy_metric(prometheus.Histogram)


def get_metrics_prefix(cls) -> str:
    return cls.metrics_prefix if hasattr(cls, 'metrics_prefix') and cls.metrics_prefix else cls.__name__.lower()


def get_or_create_metric_instance(name: str, constructor: Callable[[str], MetricType]) -> MetricType:
    global _metrics
    if name not in _metrics:
        _metrics[name] = constructor(name)
    return _metrics[name]


class metric(property):

    def __get__(self, instance, owner) -> MetricType:  # noqa
        cls = instance.__class__
        fullname = f'{get_metrics_prefix(cls)}_{self.fget.__name__}'
        return get_or_create_metric_instance(fullname, lambda name: self.fget(instance)(name))


class MeasureDuration:
    def __init__(self, prefix: str, labels: Optional[dict[str, str]] = None):
        self._prefix = prefix
        self.start_time = None
        self.elapsed_time = None
        self._labels = {}
        self._label_names = set()
        if labels:
            self.with_labels(labels)

    @property
    def in_progress_gauge(self) -> prometheus.Gauge:
        return get_or_create_metric_instance(f'{self._prefix}_in_progress',
                                             lambda name: prometheus.Gauge(name=name,
                                                                           documentation="Currently in progress",
                                                                           labelnames=self._label_names,
                                                                           multiprocess_mode='livesum'))

    @property
    def total_counter(self) -> prometheus.Counter:
        return get_or_create_metric_instance(f'{self._prefix}_total',
                                             lambda name: prometheus.Counter(name=name,
                                                                             documentation="Total count",
                                                                             labelnames=self._label_names))

    @property
    def duration_histogram(self) -> prometheus.Histogram:
        return get_or_create_metric_instance(f'{self._prefix}_duration',
                                             lambda name: prometheus.Histogram(name=name,
                                                                               documentation="Duration, in seconds",
                                                                               labelnames=self._label_names,
                                                                               buckets=DEFAULT_BUCKETS))

    def with_labels(self, labels: dict[str, str]) -> Self:
        self._labels = labels
        self._label_names = set(labels.keys())
        return self

    def update_labels(self, **kwargs) -> Self:
        for (key, value) in kwargs.items():
            self._labels[key] = value
            self._label_names.add(key)
        return self

    def __enter__(self):
        self.in_progress_gauge.labels(**self._labels).inc()
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_time = time.perf_counter() - self.start_time
        self.in_progress_gauge.labels(**self._labels).dec()
        self.total_counter.labels(**self._labels).inc()
        self.duration_histogram.labels(**self._labels).observe(time.perf_counter() - self.start_time)

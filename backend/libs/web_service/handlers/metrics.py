from http import HTTPStatus

from prometheus_client import CollectorRegistry, generate_latest, multiprocess
from starlette.responses import PlainTextResponse

from ..dependencies import basic_auth_security


def default_metrics_handler(secure=basic_auth_security):
    return PlainTextResponse(generate_latest(), status_code=HTTPStatus.OK.value)


def multi_process_metrics_handler(secure=basic_auth_security):
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)

    app_metrics = generate_latest(registry)
    return PlainTextResponse(app_metrics, status_code=HTTPStatus.OK.value)


def add_metrics_handler(router, path='/metrics', handler=default_metrics_handler):
    router.add_api_route(
        path=path,
        methods=["GET"],
        description="Prometheus-compatible application metrics",
        endpoint=handler,
    )

from http import HTTPStatus

from prometheus_client.exposition import generate_latest
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from ..dependencies import basic_auth_security


def health_handler(registry: "HealthRegistry"):  # noqa
    """
    Ready-to-use prometheus-compatible endpoint handler

    Usage:
        health_registry = HealthRegistry(*checks, app_name='Awesome Service')
        router.add_api_route(
            path="/health",
            methods=["GET"],
            description="Prometheus-compatible state of all dependent services and overall service health",
            endpoint=health_handler(health_registry)
        )
    """
    async def handler(request: Request, secure=basic_auth_security):
        await registry.run(request)

        return PlainTextResponse(
            content=generate_latest(registry),
            status_code=HTTPStatus.OK.value,
        )
    return handler


def add_health_handler(router, registry: "HealthRegistry", path='/health', handler=health_handler):  # noqa
    handler_func = handler(registry)
    router.add_api_route(
        path=path,
        methods=["GET"],
        description="Prometheus-compatible state of all dependent services and overall service health",
        endpoint=handler_func,
    )
    return handler_func

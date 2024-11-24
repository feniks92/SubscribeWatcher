from typing import Callable, Optional

from fastapi import APIRouter

from .health import add_health_handler
from .health import health_handler as default_health_handler
from .metrics import add_metrics_handler, default_metrics_handler
from .status import add_status_handler


def add_tooling_handlers(health_registry, *,
                         status_path: str = '/status',
                         metrics_path: str = '/metrics',
                         metrics_handler: Callable = default_metrics_handler,
                         health_path: str = '/health',
                         health_handler: Callable = default_health_handler,
                         docs_root_path: str = '/api/v1/',
                         router_prefix: str = '',
                         router_tags: Optional[list[str]] = None,
                         env_prefix='SUBWTCH') -> APIRouter:
    router = APIRouter(prefix=router_prefix,
                       tags=router_tags or ['tooling'])

    add_status_handler(router,
                       path=status_path,
                       docs_root_path=docs_root_path,
                       env_prefix=env_prefix)

    add_metrics_handler(router,
                        path=metrics_path,
                        handler=metrics_handler)

    add_health_handler(router,
                       path=health_path,
                       registry=health_registry,
                       handler=health_handler)

    return router

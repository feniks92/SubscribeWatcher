from contextlib import suppress
from typing import Iterable, Optional

from fastapi import FastAPI
from starlette.types import Scope
from starlette_exporter import \
    PrometheusMiddleware as StarlettePrometheusMiddleware
from starlette_exporter.middleware import get_matching_route_path

import libs.web_service.middleware.rfc7807 as rfc7807_middleware
from libs.config import settings

from ..exception_handlers import log_error_hook
from .api_logging import ApiLoggingMiddleware
from .exception_middleware import ExceptionMiddleware
from .headers_parser import RequestHeadersMiddleware

DEFAULT_SKIP_PATHS = [
    '/',
    '/status',
    '/health',
    '/metrics',
    '/api/v1/',
    '/api/v1/docs',
    '/api/v1/openapi.json',
    '/api/v2/',
    '/api/v2/docs',
    '/api/v2/openapi.json',
    '/docs',
    '/openapi.json',
]


class PrometheusMiddleware(StarlettePrometheusMiddleware):
    # Starlette exporter has bug with metrics https://github.com/stephenhillier/starlette_exporter/issues/53
    # FastAPI does not fill app.root_path
    @staticmethod
    def _get_router_path(scope: Scope) -> Optional[str]:
        if not (scope.get("endpoint", None) and scope.get("router", None)):
            return None

        root_path = scope.get("root_path", "")
        app_root_path = scope.get("app_root_path", "")
        if app_root_path and root_path.startswith(app_root_path):
            root_path = root_path[len(app_root_path):]

        base_scope = {
            "type": scope.get("type"),
            "path": root_path + scope.get("path"),
            "path_params": scope.get("path_params", {}),
            "method": scope.get("method"),
        }

        with suppress(Exception):
            return get_matching_route_path(base_scope, scope.get("router").routes)
        return None


def add_common_middlewares(app: FastAPI,
                           metrics_prefix: Optional[str] = None,
                           skip_paths: Optional[Iterable[str]] = None):
    """
    Add middlewares for every route in the app
    """
    rfc7807_middleware.register(app, pre_hooks=(log_error_hook,), add_schema=True)
    if settings.FEATURES.HIDE_500_DESCRIPTION:
        app.add_middleware(ExceptionMiddleware)

    # add_middleware inserts middleware to top
    app.add_middleware(RequestHeadersMiddleware)

    skip_paths_ = [*DEFAULT_SKIP_PATHS]
    if skip_paths:
        skip_paths_.extend(skip_paths)

    app.add_middleware(
        ApiLoggingMiddleware,
        debug=settings.get('DEBUG', False),
        clean_headers=settings.get('LOG', {}).get('CLEAN_HEADER_IN_EXTRA', True),
        restricted_headers=['acc_t', 'Authorization', 'userId', 'u'],
        restricted_header_values=['acc_t'],
        skip_paths=skip_paths_,
    )
    app_name = app.extra['app_name']
    app.add_middleware(
        PrometheusMiddleware,
        app_name=app_name,
        prefix=metrics_prefix or app_name,
        group_paths=True,
        filter_unhandled_paths=True,
        skip_paths=skip_paths_,
        always_use_int_status=True,
    )


def add_public_middlewares(app: FastAPI):
    """
    Add middlewares for public routes
    """
    rfc7807_middleware.register(app, pre_hooks=(log_error_hook,), add_schema=True)


def add_internal_middlewares(app: FastAPI):
    """
    Add middlewares for internal routes
    """
    rfc7807_middleware.register(app, pre_hooks=(log_error_hook,), add_schema=True)

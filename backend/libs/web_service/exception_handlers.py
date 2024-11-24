from typing import Callable

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.routing import Mount

from libs import logging

log = logging.getLogger('exception_handler')


async def validation_error_callback(request: Request, exc: RequestValidationError):
    """
    Return HTTP 422 on validation errors
    """
    return await request_validation_exception_handler(request, exc)


def add_validation_error_handler(app: FastAPI):
    """
    Add validation error handler to current app and all mounted sub-applications
    N.B.: MUST be called after mounting all sub-applications
    """
    _add_handler_recursively(app, RequestValidationError, validation_error_callback)


def _add_handler_recursively(app: FastAPI, exc_cls: type, handler: Callable):
    """
    Add handler for current app and all mounted sub-applications
    """
    app.add_exception_handler(exc_cls, handler)
    for route in app.routes:
        if isinstance(route, Mount):
            _add_handler_recursively(route.app, exc_cls, handler)


def log_error_hook(request: Request, exc: Exception):
    log.critical('Internal server error', exc_info=logging.exc_info(exc))

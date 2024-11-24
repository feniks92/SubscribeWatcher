from typing import Awaitable, Callable

from starlette.middleware.base import \
    BaseHTTPMiddleware as StarlettBaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from libs import logging

Send = Callable[[Request], Awaitable[Response]]

log = logging.getLogger('middleware')


class BaseHTTPMiddleware(StarlettBaseHTTPMiddleware):

    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        except RuntimeError as exc:
            if str(exc) == 'No response returned.':
                request = Request(scope, receive=receive)
                if await request.is_disconnected():
                    log.info("Remote client disconnected")
                    return
            raise

    async def dispatch(self, request, call_next):
        raise NotImplementedError()

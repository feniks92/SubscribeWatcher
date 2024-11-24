import uuid
from contextvars import ContextVar
from typing import Type

import pydantic
from fastapi.exception_handlers import request_validation_exception_handler
from pydantic import BaseModel, Field, ValidationError
from starlette.requests import Request
from starlette.responses import Response

from libs import logging

from .base import BaseHTTPMiddleware, Send
from .exceptions import HeaderValidationError

request_id = ContextVar('request_id')


class DefaultHeadersModel(BaseModel):
    request_id: str | None = Field(None, alias='x-request-id')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.request_id:
            rq_headers = [hdr for hdr in ('rqid', 'requestid') if hdr in kwargs]
            self.request_id = kwargs.get(next(iter(rq_headers))) if rq_headers else str(uuid.uuid4())
        request_id.set(self.request_id)

    def dict(self, *args, **kwargs):
        if pydantic.__version__.startswith('2.'):
            return super().model_dump(*args, by_alias=True, exclude_none=True, **kwargs)
        else:
            return super().model_dump(*args, by_alias=True, exclude_none=True, **kwargs)


class HeaderChecker:

    def __init__(self, model):
        self._headers_model = model or DefaultHeadersModel

    async def process_before(self, request):
        hdr_dict = {hdr.lower(): value for hdr, value in request.headers.items()}
        try:
            request.state.headers = self._headers_model(**hdr_dict)
        except ValidationError as exc:
            return await request_validation_exception_handler(request, HeaderValidationError(exc))

        for name, _ in request.state.headers.model_fields.items():
            logging.context.set(name, getattr(request.state.headers, name))

    @staticmethod
    def process_after(request, response):
        response.headers.update(request.state.headers.dict())
        return response


class RequestHeadersMiddleware(BaseHTTPMiddleware):

    def __init__(self, model: Type[BaseModel] | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checker = HeaderChecker(model=model or DefaultHeadersModel)

    async def dispatch(self, request: Request, call_next: Send) -> Response:
        response = await self.checker.process_before(request)
        if response:
            return response
        response = await call_next(request)
        return self.checker.process_after(request, response)


def get_request_id():
    # get ContextVar value, default is supposed to be used in tests
    return request_id.get('')

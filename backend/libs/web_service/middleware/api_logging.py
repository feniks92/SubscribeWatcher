from typing import List, Optional, Union

from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.responses import Response

from libs import logging
from libs.utils.time import elapsed_time

from .base import BaseHTTPMiddleware, Send

RESTRICTED_HEADER_PLACEHOLDER = '*' * 6

logger = logging.getLogger('api')


class ApiLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self,
                 debug: bool = False,
                 clean_headers: bool = False,
                 skip_paths: Optional[List[str]] = None,
                 restricted_headers: Optional[List[str]] = None,
                 restricted_header_values: Optional[List[str]] = None,
                 *args, **kwargs,
                 ):
        self.debug = debug
        self.clean_headers = clean_headers
        self.restricted_headers = []
        if restricted_headers is not None:
            self.restricted_headers = [hdr.lower() for hdr in restricted_headers]
        self.restricted_header_values = []
        if restricted_header_values is not None:
            self.restricted_header_values = [hdr.lower() for hdr in restricted_header_values]
        self.skip_paths = []
        if skip_paths is not None:
            self.skip_paths = skip_paths
        super().__init__(*args, **kwargs)

    @staticmethod
    def _request_url(request: Request) -> str:
        return f"{request.url.path}?{request.url.query}" if request.url.query else request.url.path

    @staticmethod
    def _response_body(response: Response) -> str:
        if hasattr(response, "body"):
            return response.body
        if hasattr(response, 'text'):
            return response.text
        if hasattr(response, 'content'):
            return response.content
        return ""

    async def dispatch(self, request: Request, call_next: Send) -> Response:
        if request.url.path in self.skip_paths:
            return await call_next(request)

        elapsed = elapsed_time()
        _ = next(elapsed)
        url = self._request_url(request)
        logger.info("Service request",
                    extra={"method": request.method,
                           "url": {'full': url}})
        logger.debug("Service request details",
                     extra={"method": request.method,
                            "url": {'full': url},
                            "headers": dict(**request.headers)})
        response = await call_next(request)
        response_time = next(elapsed)

        if 200 <= response.status_code < 300:
            logger.info("Service response",
                        extra={"method": request.method,
                               "url": {'full': url},
                               "status_code": response.status_code,
                               "response_time": response_time})
            logger.debug("Service response details",
                         extra={"url": {'full': url},
                                "status_code": response.status_code,
                                "headers": dict(**response.headers)})
        if response.status_code == 401:
            pass
        if 402 <= response.status_code < 600:
            logger.error("Service response",
                         extra={"method": request.method,
                                "url": {'full': url},
                                "headers": self._clean_headers(request.headers),
                                "status_code": response.status_code,
                                "response_time": response_time})
            logger.debug("Service response details",
                         extra={"url": {'full': url},
                                "body": self._response_body(response)})
        return response

    def _clean_header(self, item: tuple[str, str]) -> tuple[str, str]:
        key, value = item
        if key in self.restricted_headers:
            return key, RESTRICTED_HEADER_PLACEHOLDER

        for val in self.restricted_header_values:
            if val in value:
                return key, RESTRICTED_HEADER_PLACEHOLDER

        return key, value

    def _clean_headers(self, headers: Headers) -> Union[dict[str, str], Headers]:
        return dict(map(self._clean_header, headers.items())) if self.clean_headers else headers

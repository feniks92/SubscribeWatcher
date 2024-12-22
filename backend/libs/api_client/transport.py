import asyncio
from asyncio.exceptions import TimeoutError
from json import JSONDecodeError

import pydantic
from httpx import AsyncHTTPTransport, Request, Response, ResponseNotRead, TimeoutException

from .exceptions import RetryAttemptsOutError
from .utils import LOGGER

from pydantic import TypeAdapter

from .models import ApiRetrySettings


class AsyncRetryTransport(AsyncHTTPTransport):
    RETRYABLE_METHODS = frozenset(
        ["HEAD", "GET", "POST", "PUT", "DELETE"]
    )

    def __init__(self, config: ApiRetrySettings, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    async def _extract_json(self, response: Response) -> dict:
        content_type = response.headers.get('content-type', '')
        if 'application/json' not in content_type:
            return {}
        try:
            return response.json()
        except (UnicodeDecodeError, JSONDecodeError):
            return {}
        except ResponseNotRead:
            await response.aread()
            return await self._extract_json(response)
        except Exception:  # noqa
            return {}

    def _check_status_code_trigger(self, response: Response) -> bool:
        if self.config.TRIGGER.STATUS_CODES:
            return response.status_code not in self.config.TRIGGER.STATUS_CODES
        return True

    async def _check_body_trigger(self, response: Response) -> bool:
        if self.config.TRIGGER.BODY:
            data = await self._extract_json(response)
            LOGGER.info('Retry body trigger content', extra={"content": str(data)})
            if not data:
                return False
            try:
                if pydantic.__version__.startswith('2.'):
                    TypeAdapter(self.config.TRIGGER.BODY).validate_python(data)
                else:
                    parse_obj_as(self.config.TRIGGER.BODY, data)

                return True
            except ValueError:
                return False
        return True

    async def _send(self, request: Request) -> Response | None:
        try:
            response = await super().handle_async_request(request)
            if not self._check_status_code_trigger(response):
                LOGGER.info('Retry by status codes trigger', extra={"status_code": response.status_code})
                return None

            check_result = await self._check_body_trigger(response)
            if not check_result:
                LOGGER.info('Retry by body trigger')
                return None
            return response
        except TimeoutException:
            if not self.config.TRIGGER.TIMEOUT:
                raise
            LOGGER.info('Retry by timeout trigger')
        except Exception as e:  # noqa
            if not self.config.TRIGGER.EXCEPTION:
                raise
            LOGGER.info('Retry by exception trigger', extra={'exc': e.__class__.__name__})

    async def handle_async_request(self, request: Request) -> Response:
        try:
            async with asyncio.timeout(self.config.TIMEOUT):
                return await self._process_request_attempts(request)
        except TimeoutError as e:
            raise TimeoutException('Timeout for attempts') from e

    async def _process_request_attempts(self, request: Request) -> Response:
        for attempt in range(self.config.ATTEMPTS):
            LOGGER.info("Request attempt with retries",
                        extra={'count': attempt, 'url': {"full": str(request.url)}})

            response = await self._send(request)
            if response:
                return response

            await asyncio.sleep(self.config.DELAY)

        raise RetryAttemptsOutError.for_request(request=request)

import inspect
from json import JSONDecodeError
from typing import Any, Type

import httpx
import pydantic
from dynaconf.utils.boxing import DynaBox
from httpx import Timeout
from pydantic import BaseModel, ValidationError

from pydantic import TypeAdapter


from libs import metrics
from libs.config import settings

from .utils import LOGGER

try:
    from shared.unleash import feature
except ImportError:
    feature = None

from .api_client import ApiClientInterface, T
from .exceptions import (ExpectedClientError, ResponseHandlingException, ResponseValidationException,
                         ServiceTemporaryDisabled, TimeoutClientError, UnexpectedResponse)

from .models import ApiClientSettings, ApiIntegrationSettings

from .registry import HttpTransportRegistry


class ApiClient(ApiClientInterface):
    """ApiClient uses multiple HTTP connections"""

    def __init__(self, config: ApiIntegrationSettings):
        super().__init__(config)
        self._labels = {}
        self.service_name = config.SERVICE_NAME
        self.metrics_prefix = config.metrics_prefix
        self.extra_labels = dict(config.EXTRA_LABELS)

    @metrics.metric
    def request_contract_errors_total(self):
        return metrics.Counter("Total HTTP request contract errors", labelnames=('method', 'path'), )

    def _build_request_url(self, path: str, path_params: dict[str, Any] | None = None) -> str:
        base = str(self.get_base_url())
        path_ = path.format(**path_params) if path_params else path
        return "/".join((base.rstrip('/'), path_.lstrip('/')))

    def _get_transport(self, url: str) -> httpx.AsyncBaseTransport:
        transport = HttpTransportRegistry.get(url)
        if transport:
            return transport

        if self.config.RETRY:
            transport = HttpTransportRegistry.create_retriable_transport(self.config.RETRY)
        else:
            transport = HttpTransportRegistry.create_default_transport()

        if self.config.PERSISTENT_HTTP_TRANSPORT:
            return HttpTransportRegistry.put(url, transport)

        return transport

    def _check_integration_status(self):
        if feature and feature.is_enabled(f'DISABLED_INTEGRATION_{self.metrics_prefix.upper()}',
                                          context={"userId": self.service_name}, default=False):
            raise ServiceTemporaryDisabled()

    def _create_client(self, url: str) -> httpx.AsyncClient:
        default_settings = ApiClientSettings(**settings.get("ASYNC_API_CLIENT", {})).dict(by_alias=True)
        return httpx.AsyncClient(auth=self.config.auth,
                                 transport=self._get_transport(url),
                                 **default_settings)

    async def request(
            self,
            *,
            type_: Type[T],
            method: str,
            url: str | None = None,
            path_params: dict[str, Any] | None = None,
            **kwargs
    ) -> T:
        self._check_integration_status()
        path_ = url or self.config.URL
        url_tmpl = self._build_request_url(path=path_)
        self._labels = {
            "method": method,
            "url": {'full': url_tmpl},
            "service": self.service_name,
            'status_code': 0,
            **self.extra_labels,
        }
        client = self._create_client(url_tmpl)
        request = client.build_request(method,
                                       url=url_tmpl.format(**path_params) if path_params else url_tmpl,
                                       timeout=Timeout(timeout=self.config.TIMEOUT),
                                       **kwargs)

        response = await self.send(client, request)

        try:
            result = self._prepare_result(type_, response)
            LOGGER.info("Successful response",
                        extra={**self._labels,
                               "url": {'full': str(request.url)},
                               "elapsed_time": response.elapsed})
            return result
        except ValidationError as e:
            self.request_contract_errors_total.labels(**self._labels).inc()
            LOGGER.error(f"{self} response validation error",
                         extra={**self._labels,
                                "url": {'full': str(request.url)},
                                "elapsed_time": response.elapsed,
                                "error": str(e)})
            LOGGER.debug(f"{self} response validation error",
                         extra={"method": request.method,
                                "url": {'full': str(request.url)},
                                "elapsed_time": response.elapsed,
                                "content": response.content})
            raise ResponseValidationException(e) from e

    @staticmethod
    def _extract_json(response: httpx.Response) -> dict:
        try:
            return response.json()
        except (UnicodeDecodeError, JSONDecodeError):
            return {}

    @classmethod
    def _prepare_result(cls, type_: Type[T], response: httpx.Response) -> T:
        if type_ is str:
            return response.text
        if type_ is dict:
            return cls._extract_json(response)
        if inspect.isclass(type_):
            if type_ is BaseModel or issubclass(type_, BaseModel):
                return TypeAdapter(type_).validate_python(response.json())
            if type_ is httpx.Response or issubclass(type_, httpx.Response):
                return response
        return {'status_code': response.status_code,
                'headers': str(dict(response.headers)),
                'cookies': str(dict(response.cookies)),
                'content': str(cls._extract_json(response))}

    async def _send(self,
                    client: httpx.AsyncClient,
                    request: httpx.Request) -> httpx.Response:
        try:
            response = await client.send(request)
        except httpx.TimeoutException as err:
            LOGGER.warning(f"{self} response timeout", extra=self._labels)
            raise TimeoutClientError.for_request(request) from err
        except BaseException as e:
            LOGGER.info(f"{self} response exception", exc_info=True, extra=self._labels)
            raise ResponseHandlingException(e)
        return response

    async def send(self, client: httpx.AsyncClient, request: httpx.Request) -> httpx.Response:
        LOGGER.info(f"{self} send request", extra=self._labels)
        LOGGER.debug(f"{self} send request",
                     extra={**self._labels,
                            "headers": str(dict(request.headers)),
                            "url": {"full": str(request.url)},
                            "content": request.content})

        measure = metrics.MeasureDuration(prefix=self.metrics_prefix)
        with measure.with_labels(labels=self._labels):
            response = await self._send(client, request)
            measure.update_labels(status_code=response.status_code)

        if response.status_code in self.config.SUCCESS_STATUS_CODES:
            response.elapsed = measure.elapsed_time
            return response

        if response.status_code in self.config.SILENCE_STATUS_CODES:
            raise ExpectedClientError.for_response(response)

        LOGGER.info(f"{self} unexpected response", extra={**self._labels,
                                                          "elapsed_time": measure.elapsed_time,
                                                          "error": {"message": response.reason_phrase},
                                                          "content": response.text})

        raise UnexpectedResponse.for_response(response)

    @classmethod
    def create(cls, config: DynaBox) -> ApiClientInterface:
        return cls(config=ApiIntegrationSettings(**config))

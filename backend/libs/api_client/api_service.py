import asyncio
from typing import Optional, Type

from .models import Authorization, BaseRequest  # noqa

from .api_client import ApiClientInterface, T
from .utils import LOGGER


class ApiService:
    """ Basic class for api-service integrations """
    client: ApiClientInterface = None
    request_type: Type[BaseRequest] = None
    response_type: Type[T] = None

    def __init__(self):
        self.service_name = self.client.config.SERVICE_NAME
        self.url = self.client.config.URL

    async def get_response(self, method: str = "GET", type_: Type[T] = None, url: str | None = None,
                           **kwargs) -> T:
        return await self._request(method=method, type_=type_, url=url, raise_exception=True, return_exception=False,
                                   **kwargs)

    async def get_response_or_none(self, method: str = "GET", type_: Type[T] = None, url: str | None = None,
                                   **kwargs) -> Optional[T]:
        return await self._request(method=method, type_=type_, url=url, raise_exception=False, return_exception=False,
                                   **kwargs)

    async def get_response_or_error(self, method: str = "GET", type_: Type[T] = None, url: str | None = None,
                                    **kwargs) -> T | Exception:
        return await self._request(method=method, type_=type_, url=url, raise_exception=False, return_exception=True,
                                   **kwargs)

    async def send_in_background(self, method: str = "GET", type_: Type[T] = None, url: str | None = None,
                                 **kwargs) -> None:
        asyncio.create_task(self._request(method=method, type_=type_, url=url,
                                          raise_exception=False, return_exception=False,
                                          **kwargs))

    async def _request(self, method: str = "GET", type_: Type[T] = None, url: str | None = None,
                       raise_exception: bool = True, return_exception: bool = False,
                       **kwargs) -> T | Exception | None:
        request_params = self.request_type(**kwargs).to_dict() if self.request_type else kwargs
        response_type = type_ or self.response_type
        url_ = url or self.url

        try:
            return await self.client.request(
                type_=response_type,
                method=method,
                url=url_,
                **request_params
            )
        except Exception as err:
            LOGGER.warning('ApiService. Request failed',
                           extra={'source': self.service_name, 'url': {'full': url_}, 'error_message': str(err)})
            if raise_exception:
                raise
            if return_exception:
                return err
            return None

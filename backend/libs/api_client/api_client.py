import abc
from typing import Any, Type

import httpx
from pydantic import BaseModel

from libs import logging

from .models import ApiIntegrationSettings


logger = logging.getLogger(__name__)

T = str | dict | BaseModel | httpx.Response | None


class ApiClientInterface:
    """ApiClient uses multiple HTTP connections"""

    _path: str = ""

    def __init__(self, config: ApiIntegrationSettings):
        self.config = config
        self._base_url = httpx.URL(config.BASE_URL)

    def get_base_url(self) -> httpx.URL:
        return self._base_url

    @abc.abstractmethod
    async def request(
            self,
            *,
            type_: Type[T],
            method: str,
            url: str,
            path_params: dict[str, Any] | None = None,
            **kwargs
    ) -> T:
        pass

    @abc.abstractmethod
    async def send(self, client: httpx.AsyncClient,
                   request: httpx.Request) -> httpx.Response:
        pass

    def __str__(self):
        return self.__class__.__name__

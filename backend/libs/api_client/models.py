import importlib
from dataclasses import asdict, fields
from typing import List, Optional, Type, Union

from fastapi.params import Body, Cookie, Header, Path, Query
from httpx import Limits, Timeout
from pydantic import BaseModel, Field, field_validator
from pydantic.dataclasses import dataclass


@dataclass
class BaseDataclass:
    def to_dict(self, by_alias: bool = True):
        base_dict = asdict(self)
        if by_alias:
            aliases = ((field.name, field.default.alias) for field in fields(self) if field.default.alias)
            for alias in aliases:
                base_dict[alias[1]] = base_dict.pop(alias[0])

        return base_dict


class ApiTransportSettings(BaseModel):
    VERIFY: bool = Field(False, alias='verify')
    MAX_CONNECTIONS: int = Field(100, exclude=True)
    MAX_KEEPALIVE_CONNECTIONS: int = Field(20, exclude=True)
    KEEPALIVE_EXPIRY: float = Field(5, exclude=True)

    def dict(self, **kwargs) -> dict:
        result = super().model_dump(**kwargs)
        result['limits'] = Limits(
            max_connections=self.MAX_CONNECTIONS,
            max_keepalive_connections=self.MAX_KEEPALIVE_CONNECTIONS,
            keepalive_expiry=self.KEEPALIVE_EXPIRY,
        )
        return result


class ApiClientSettings(BaseModel):
    TIMEOUT: float = Field(5, description='', exclude=True)
    FOLLOW_REDIRECTS: bool = Field(False, alias='follow_redirects')
    MAX_REDIRECTS: int = Field(20, alias='max_redirects')

    def dict(self, **kwargs) -> dict:
        result = super().model_dump(**kwargs)
        result['timeout'] = Timeout(self.TIMEOUT)
        return result


class ApiRetryTriggerSettings(BaseModel):
    STATUS_CODES: list[int] = Field([408, 500, 503],
                                    description='Список статусов по которым происходит повторная отправка')
    BODY: Optional[Type[BaseModel]] = Field(None, description='Модель для валидации содержимого ответа')
    TIMEOUT: bool = Field(True, description='Делать повторные запросы при таймаутах')
    EXCEPTION: bool = Field(False, description='Делать повторные запросы при исключениях в процессе отправки')

    @field_validator('BODY', mode="before")
    @classmethod
    def body_trigger_import(cls, value: str | Type[BaseModel] | None):
        if value:
            if isinstance(value, str):
                module, _, class_name = value.rpartition('.')
                return getattr(importlib.import_module(module), class_name)
        return value


class ApiRetrySettings(BaseModel):
    ATTEMPTS: int = Field(3, description='Кол-во попыток повторных отправок')
    DELAY: float = Field(1.0, description='Период ожидания между попытками')
    TRIGGER: ApiRetryTriggerSettings = Field(..., description='Триггеры повторных отправок')
    TIMEOUT: Optional[float] = Field(None, description='Общий таймаут на все попытки')


class ApiIntegrationSettings(BaseModel):
    SERVICE_NAME: str = Field(..., description='Имя сервиса для интеграции')
    METRICS_PREFIX: str = Field(None, description='Префикс в метриках')
    BASE_URL: str = Field(..., description='Базовая часть url сервиса')
    URL: Optional[str] = Field(None, description='Путь до сервиса интеграции')
    TIMEOUT: float = Field(1.0, description='Таймаут подключения к сервису')
    SUCCESS_STATUS_CODES: list[int] = Field([200, 201, 204], description='Список успешных HTTP-кодов ответа сервиса')
    SILENCE_STATUS_CODES: Optional[list[int]] = Field([], description='Список HTTP-кодов ответа сервиса,'
                                                                      'для которых не будет генерироваться исключение')
    RETRY: Optional[ApiRetrySettings] = Field(None)
    VERIFY: bool = Field(False, description='Необходимость проверки ssl-сертификата')
    EXTRA_LABELS: Optional[dict] = Field({}, description='Дополнительные метки для метрик')
    USERNAME: str | None = Field(None)
    PASSWORD: str | None = Field(None)
    PERSISTENT_HTTP_TRANSPORT: bool = Field(True, description='Необходимость кеширования транспорта')

    @property
    def metrics_prefix(self) -> str:
        return self.METRICS_PREFIX or self.SERVICE_NAME.lower().replace('-', '_').replace(' ', '_')

    @property
    def auth(self) -> tuple | None:
        if self.USERNAME and self.PASSWORD:
            return self.USERNAME, self.PASSWORD


class Authorization(Header):
    pass


_allowed_request_types = Union[Authorization, Header, Query, Path, Cookie, Body]


@dataclass(config={'populate_by_name': True})
class BaseRequest(BaseDataclass):
    """
    Target request need to be pydantic dataclass and contain attributes of types:
    Path, Cookie, Param, Body, Authorization(only one).
    Example:
        @dataclass(config={'populate_by_name': True})
        class ExampleRequest(BaseRequest):
            acc_t: str = Cookie("")
            user_id: str = Path("", alias="userId")
    """

    def to_dict(self, by_alias: bool = True):
        path_params: dict = {}
        params: dict = {}
        cookies: dict = {}
        headers: dict = {}
        json: dict = {}
        for field in fields(self):
            if isinstance(field.default, _allowed_request_types):
                if by_alias:
                    key = field.default.alias or field.name
                else:
                    key = field.name
                value = getattr(self, field.name)

                if isinstance(field.default, Authorization):
                    headers["Authorization"] = f"Bearer {value}"
                elif isinstance(field.default, Header):
                    headers[key] = value
                elif isinstance(field.default, Query):
                    if isinstance(value, List):
                        value = ",".join(str(v) for v in value)
                    params[key] = value
                elif isinstance(field.default, Path):
                    path_params[key] = value
                elif isinstance(field.default, Cookie):
                    cookies[key] = value
                elif isinstance(field.default, Body):
                    json[key] = value

        output = {}
        if path_params:
            output["path_params"] = path_params
        if params:
            output["params"] = params
        if cookies:
            output["cookies"] = cookies
        if headers:
            output["headers"] = headers
        if json:
            output["json"] = json

        return output

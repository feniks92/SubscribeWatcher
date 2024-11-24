from datetime import datetime, timezone
from typing import Any, Self

from pydantic import BaseModel, Field, PrivateAttr, validator

from libs.config import settings
from libs.logging import context


def set_request_id():
    return context.get().get('request_id')


def set_session_id():
    return context.get().get('session_id')


def set_user_id():
    return context.get().get('user_id')


def set_surface_id():
    return context.get().get('surface_id')


def set_context():
    return context.get_service_context() or {}


class LogBase(BaseModel):

    @classmethod
    def create_or_none(cls, **kwargs) -> Self | None:
        instance = cls(**kwargs)
        if instance and instance.dict():
            return instance
        return None

    def dict(self, *args, **kwargs):
        kwargs = {'exclude_none': True, **kwargs}
        return super().dict(*args, **kwargs)

    @validator('*')
    def exclude_empty(cls, values):
        if isinstance(values, dict):
            return {k: v for k, v in values.items() if v}
        return values


class LogExtraBaseLabels(LogBase):
    app_name: str | None = settings.get('SERVICE', {}).get('APP_NAME')
    env: str = settings.current_env


class LogExtraHttpRequest(LogBase):
    id: str | None = Field(default_factory=set_request_id)
    session_id: str | None = Field(default_factory=set_session_id)
    surface_id: str | None = Field(default_factory=set_surface_id)
    method: str | None
    content: dict | None

    def __bool__(self):
        return bool(self.dict(exclude_none=True))


class LogExtraHttpResponse(LogBase):
    status_code: int | None
    content: str | None
    elapsed_time: float | None

    def __bool__(self):
        return False if not self.dict(exclude_none=True) else True


class LogExtraUrl(LogBase):
    original: str | None
    full: str | None
    port: str | None
    query: str | None


class LogExtraUser(LogBase):
    id: str = Field(default_factory=set_user_id)
    hash: str | None
    name: str | None
    role: str | None
    email: str | None


class LogExtraHttp(LogBase):
    version: str | None
    request: LogExtraHttpRequest | None = Field(default_factory=LogExtraHttpRequest.create_or_none)
    response: LogExtraHttpResponse | None = Field(default_factory=LogExtraHttpResponse.create_or_none)


class LogBaseFile(LogBase):
    path: str | None


class LogFile(LogBase):
    line: str | None
    name: str | None
    function: str | None
    module: str | None


class LogOrigin(LogBase):
    file: LogFile | None


class LogExtraInfo(LogBase):
    level: str | None
    file: LogBaseFile | None = Field(default_factory=LogBaseFile.create_or_none)
    logger: str | None
    origin: LogOrigin | None = Field(default_factory=LogOrigin.create_or_none)


class LogExtraError(LogBase):
    id: str | None
    code: str | None
    message: str | None
    stack_trace: str | None
    type: str | None


class LogExtra(LogBase):
    """
        Based on ELK Common fields
        https://www.elastic.co/guide/en/ecs/current/ecs-url.html
    """
    __aliases: set[str] = set()
    __context: dict[str, Any] = PrivateAttr(default_factory=set_context)
    __additional_extra: str | None = PrivateAttr(default=None)

    tags: list[str] | None
    labels: LogExtraBaseLabels = Field(default_factory=LogExtraBaseLabels)
    timestamp: str = Field(default_factory=datetime.now(timezone.utc).isoformat)

    log: LogExtraInfo | None = Field(default_factory=LogExtraInfo.create_or_none)
    user: LogExtraUser | None
    http: LogExtraHttp | None = Field(default_factory=LogExtraHttp.create_or_none)
    url: LogExtraUrl | None = Field(default_factory=LogExtraUrl.create_or_none)

    message: str | None

    error: LogExtraError | None = Field(default_factory=LogExtraError.create_or_none)

    def __new__(cls, *args, **kwargs):
        if not cls.__aliases:
            cls.__aliases = {field.alias for field in cls.__fields__.values()}
        return super().__new__(cls)

    def __init__(self, **kwargs):
        fields = {key: value for key, value in kwargs.items() if key in self.__aliases}
        super().__init__(**fields)

        self.__context |= kwargs.pop('context', {})
        additional_extra = {key: value for key, value in kwargs.items() if key not in self.__aliases}
        self.__additional_extra = str(additional_extra) if additional_extra else None

    def dict(self, *args, **kwargs):
        result = super().dict(*args, **kwargs)
        if self.__additional_extra:
            result['additional_extra'] = self.__additional_extra
        if self.__context:
            result['context'] = self.__context
        return result

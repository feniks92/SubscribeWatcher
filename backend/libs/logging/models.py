from datetime import datetime, timezone
from typing import Any, Self

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from libs.config import settings


class LogBase(BaseModel):

    @classmethod
    def create_or_none(cls, **kwargs) -> Self | None:
        instance = cls(**kwargs)
        if instance and instance.dict():
            return instance
        return None

    def dict(self, *args, **kwargs):
        kwargs = {'exclude_none': True, **kwargs}
        return super().model_dump(*args, **kwargs)

    @field_validator('*')
    @classmethod
    def exclude_empty(cls, values):
        if isinstance(values, dict):
            return {k: v for k, v in values.items() if v}
        return values


class LogExtraBaseLabels(LogBase):
    app_name: str | None = settings.get('SERVICE', {}).get('APP_NAME')
    env: str = settings.current_env


class LogExtraHttpRequest(LogBase):
    id: str | None = None
    session_id: str | None = None
    surface_id: str | None = None
    app_platform: str | None = None
    app_version: str | None = None
    method: str | None = None
    content: dict | None = None

    def __bool__(self):
        return bool(self.dict(exclude_none=True))


class LogExtraHttpResponse(LogBase):
    status_code: int | None = None
    content: str | None = None
    elapsed_time: float | None = None

    def __bool__(self):
        return False if not self.dict(exclude_none=True) else True


class LogExtraUrl(LogBase):
    original: str | None = None
    full: str | None = None
    port: str | None = None
    query: str | None = None


class LogExtraUser(LogBase):
    id: str | None = None
    hash: str | None = None
    name: str | None = None
    role: str | None = None
    email: str | None = None


class LogExtraHttp(LogBase):
    version: str | None = None
    request: LogExtraHttpRequest | None = Field(default_factory=LogExtraHttpRequest.create_or_none)
    response: LogExtraHttpResponse | None = Field(default_factory=LogExtraHttpResponse.create_or_none)


class LogBaseFile(LogBase):
    path: str | None = None


class LogFile(LogBase):
    line: str | None = None
    name: str | None = None
    function: str | None = None
    module: str | None = None


class LogOrigin(LogBase):
    file: LogFile | None = None


class LogExtraInfo(LogBase):
    level: str | None = None
    file: LogBaseFile | None = Field(default_factory=LogBaseFile.create_or_none)
    logger: str | None = None
    origin: LogOrigin | None = Field(default_factory=LogOrigin.create_or_none)


class LogExtraError(LogBase):
    id: str | None = None
    code: str | None = None
    message: str | None = None
    stack_trace: str | None = None
    type: str | None = None


class LogExtra(LogBase):
    """
        Based on ELK Common fields
        https://www.elastic.co/guide/en/ecs/current/ecs-url.html
    """
    __context: dict[str, Any] = PrivateAttr(default_factory=dict)
    __additional_extra: str | None = PrivateAttr(default=None)

    tags: list[str] | None = None
    labels: LogExtraBaseLabels = Field(default_factory=LogExtraBaseLabels)
    timestamp: str = Field(default_factory=datetime.now(timezone.utc).isoformat)

    log: LogExtraInfo | None = Field(default_factory=LogExtraInfo.create_or_none)
    user: LogExtraUser | None = None
    http: LogExtraHttp | None = Field(default_factory=LogExtraHttp.create_or_none)
    url: LogExtraUrl | None = Field(default_factory=LogExtraUrl.create_or_none)

    message: str | None = None

    error: LogExtraError | None = Field(default_factory=LogExtraError.create_or_none)

    def __init__(self, **kwargs):
        available_fields = {
            field.alias or key
            for key, field in self.model_fields.items()
        }

        fields = {key: value for key, value in kwargs.items() if key in available_fields}
        super().__init__(**fields)

        self.__context |= kwargs.pop('context', {})
        additional_extra = {key: value for key, value in kwargs.items() if key not in available_fields}
        self.__additional_extra = str(additional_extra) if additional_extra else None

    def dict(self, *args, **kwargs):
        result = super().model_dump(*args, **kwargs)
        if self.__additional_extra:
            result['additional_extra'] = self.__additional_extra
        if self.__context:
            result['context'] = self.__context
        return result

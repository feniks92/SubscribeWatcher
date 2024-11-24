from typing import Optional

from pydantic.dataclasses import dataclass


@dataclass
class AppConfig:
    APP_NAME: str

    VERSION: Optional[str] = None
    URL_ROOT_PATH: Optional[str] = None
    METRICS_PREFIX: Optional[str] = None
    ACCESS_TOKEN_ENVIRONMENT: str | bool = False
    SHOW_API_DOCS: bool = False

    @property
    def is_root(self):
        return type(self) is AppConfig


@dataclass
class SubAppConfig(AppConfig):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.URL_ROOT_PATH = None

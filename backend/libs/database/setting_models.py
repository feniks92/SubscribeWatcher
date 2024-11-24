from pydantic import BaseModel, Field, model_validator


class BaseDbSettings(BaseModel):
    HOST: str | None = None
    CLUSTERS: list[str] = list()
    PORT: str | None = None
    USERNAME: str = ''
    PASSWORD: str = ''



class PostgresDbSettings(BaseDbSettings):
    DB_URI: str = ''
    URL: str | None = None

    @model_validator(mode='after')
    def get_url(self):
        from rfc3986 import ParseResult, urlparse
        parts = {**urlparse(self.DB_URI)._asdict(), 'userinfo': f'{self.USERNAME}:{self.PASSWORD}'}
        self.URL = ParseResult.from_parts(**parts).geturl()
        self.HOST = self.HOST or parts['host']
        self.PORT = self.PORT or parts['port']


class SqlAlchemySettings(PostgresDbSettings):
    COLLECT_METRICS: bool = Field(True, description='set to false for migrations to prevent unnecessary metrics '
                                                    'collection')
    CONNECT_TIMEOUT: int = Field(2, description='in seconds')
    ECHO: bool = False
    NO_POOLING: bool = True
    POOL_LOG: bool = Field(False, description='set "debug" for full output')
    POOL_MAX_OVERFLOW: int = Field(0, description='if you see warnings about low pool size, try to increase this value '
                                                  'instead of POOL_SIZE. Use "-1" to set unlimited overflow')
    POOL_SIZE: int = Field(20, description="don't use big values, 5 - 30 more usefull")


class AsyncPgSettings(PostgresDbSettings):
    TIMEOUT: int = 1
    CACHE_RESULT: bool = False

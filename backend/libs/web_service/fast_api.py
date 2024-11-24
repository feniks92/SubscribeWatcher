from typing import Optional, Union

from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response

from libs.config import APP_CONFIG
from libs.config.types import AppConfig, SubAppConfig
from libs.web_service.middleware import add_common_middlewares


def fast_api_fabric(config: Optional[Union[AppConfig, SubAppConfig]] = None,
                    **fast_api_settings):
    app_config = config or APP_CONFIG
    app = create_fast_api_app(config=app_config, **fast_api_settings)

    app.add_api_route(path='/',
                      endpoint=root_route(app),
                      methods=['GET'])

    if app_config.is_root:
        add_common_middlewares(app=app,
                               metrics_prefix=app_config.METRICS_PREFIX)
    return app


def create_fast_api_app(config: Union[AppConfig, SubAppConfig], **fast_api_settings):
    readable_app_name = config.APP_NAME.translate({ord('_'): ord(' '), ord('-'): ord(' ')}).capitalize()
    service_config = dict(
        app_name=config.APP_NAME,
        title=f"R&P {readable_app_name} REST API",
        description=f"REST API of {readable_app_name} of Recommendations and Personalization platform",
        version=config.VERSION,
        root_path=config.URL_ROOT_PATH,
        docs_url='/docs' if config.SHOW_API_DOCS else None,
        redoc_url='/redoc' if config.SHOW_API_DOCS else None,
        openapi_url='/openapi.json' if config.SHOW_API_DOCS else None,
    )
    fastapi_config = {**service_config, **fast_api_settings}
    return FastAPI(**fastapi_config)


def root_route(app):
    async def _set_root_route() -> Response:
        return JSONResponse(content={"message": f"{app.title} Hello"})

    return _set_root_route

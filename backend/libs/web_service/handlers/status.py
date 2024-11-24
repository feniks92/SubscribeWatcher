import os

from libs.config import settings
from libs.web_service.schemas import StatusResponse

from ..dependencies import basic_auth_security


def add_status_handler(router, path='/status',
                       docs_root_path='/api/v1/',
                       env_prefix='SUBWTCH'):
    router.add_api_route(
        path=path,
        methods=["GET"],
        response_model=StatusResponse,
        response_model_exclude_none=True,
        endpoint=status_handler_factory(docs_root_path, env_prefix)
    )


def status_handler_factory(docs_root_path, env_prefix):
    def handler(secure=basic_auth_security):
        return StatusResponse(
            version=settings.SERVICE.VERSION,
            docs={
                'swaggerUI': f'{docs_root_path}/docs',
                'redocUI': f'{docs_root_path}/redoc',
                'openapi': f'{docs_root_path}/openapi.json',
            } if settings.SERVICE.get('SHOW_API_DOCS', False) else None
        )

    return handler

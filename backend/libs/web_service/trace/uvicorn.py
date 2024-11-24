import asyncio

import aiomonitor
from uvicorn.config import Config
from uvicorn.server import Server

from libs.config import settings
from libs.logging import get_logging_config

from .app.middleware import register_middlewares
from .app.routes import add_memory_trace_app


def run_uvicorn_with_trace(app=None, **kwargs):
    if not app:
        from app.app import app

    trace_app = add_memory_trace_app()
    register_middlewares(app)

    app.mount('/api/profiling', trace_app)

    loop = asyncio.new_event_loop()
    with aiomonitor.start_monitor(loop=loop):
        config = Config(app=app,
                        host=settings.get('HOST', '0.0.0.0'),  # nosec
                        port=settings.get('PORT', 80),  # nosec
                        access_log=True,
                        debug=settings.DEBUG,
                        reload=settings.DEBUG,
                        log_config=get_logging_config(level=settings.LOG.LEVEL,
                                                      fmt=settings.LOG.FORMAT,
                                                      is_log_database=settings.LOG.get('DATABASE', False)),
                        loop='asyncio',
                        **kwargs)
        server = Server(config=config)
        func = server.serve
        loop.run_until_complete(func())


def _get_internal_router(app):
    router = [r.app for r in app.routes if 'internal' in r.path]
    return router[0] if router else app

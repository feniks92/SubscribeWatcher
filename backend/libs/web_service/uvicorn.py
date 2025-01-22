import uvicorn

from libs import logging
from libs.config import settings
from libs.logging import get_logging_config
from libs.logging.context import set_service_log_model
from libs.logging.models import LogExtra

log = logging.getLogger(__name__)


def run_uvicorn(app: str | None = None, log_model: type[LogExtra] = LogExtra, **kwargs):
    set_service_log_model(value=log_model)
    uvicorn.run(
        app=app or "app.app:app",
        host=settings.get('HOST', '0.0.0.0'),  # nosec
        port=settings.get('PORT', 80),  # nosec
        access_log=True,
        reload=settings.DEBUG,
        log_config=get_logging_config(level=settings.LOG.LEVEL,
                                      fmt=settings.LOG.FORMAT,
                                      is_log_database=settings.LOG.get('DATABASE', False)),
        **kwargs
    )

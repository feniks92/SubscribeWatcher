from app.tooling.routes import router as tooling
from app.v1.app import app as watcher_v1
from libs import logging
from libs.api_client.registry import HttpTransportRegistry
from libs.web_service.exception_handlers import add_validation_error_handler
from libs.web_service.fast_api import fast_api_fabric

logger = logging.getLogger(__name__)

app = fast_api_fabric()

app.mount('/api/v1', watcher_v1)
app.include_router(tooling)

add_validation_error_handler(app)


@app.on_event("startup")
async def startup():
    logger.info(f'{app.title}: STARTED')


@app.on_event("shutdown")
async def shutdown():
    await HttpTransportRegistry.close_all()
    logger.info(f'{app.title}: STOPPED')

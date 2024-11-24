from app.v1.subscribe_watcher import routes as subs_watcher
from libs.config import SUB_APP_CONFIG
from libs.web_service.fast_api import fast_api_fabric
from libs.web_service.middleware import add_public_middlewares

SUB_APP_CONFIG.APP_NAME = 'watcher_v1'

app = fast_api_fabric(config=SUB_APP_CONFIG)

add_public_middlewares(app)

app.include_router(subs_watcher.router)

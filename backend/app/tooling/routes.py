from libs.database.sql_alchemy import db_bound
from libs.web_service.handlers import add_tooling_handlers
from libs.web_service.handlers.health import health_handler

from .healthcheck import health_registry

router = add_tooling_handlers(health_registry,
                              docs_root_path='/api/v1/',
                              health_handler=lambda registry: db_bound(health_handler(registry)))

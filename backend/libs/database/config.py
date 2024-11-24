from libs.config import settings
from libs.database.setting_models import AsyncPgSettings, SqlAlchemySettings

db_settings = settings.get('DATABASE', {})
sqlalchemy_settings = SqlAlchemySettings(**db_settings)
asyncpg_settings = AsyncPgSettings(**db_settings)

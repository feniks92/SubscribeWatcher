import random
import string

from shared.config import settings
from shared.database.setting_models import SqlAlchemySettings

random.seed()


def test_sqlalchemy_url_builder(patch_settings):
    username = 'root'
    password = ''.join(random.choices(string.ascii_lowercase, k=8))
    with patch_settings({
        'DATABASE.DB_URI': 'postgresql+asyncpg:///database?host=1.1.1.1:5432&host=1.1.1.1:5432',
        'DATABASE.USERNAME': username,
        'DATABASE.PASSWORD': password
    }):
        assert (SqlAlchemySettings(**settings.get('DATABASE', {})).URL ==
                f'postgresql+asyncpg://{username}:{password}@/database?host=1.1.1.1:5432&host=1.1.1.1:5432')

    with patch_settings({
        'DATABASE.DB_URI': 'postgresql+asyncpg://db:5432/database',
        'DATABASE.USERNAME': username,
        'DATABASE.PASSWORD': password
    }):
        assert (SqlAlchemySettings(**settings.get('DATABASE', {})).URL ==
                f'postgresql+asyncpg://{username}:{password}@db:5432/database')

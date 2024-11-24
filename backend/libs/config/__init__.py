from dynaconf import Dynaconf

from libs.config.types import AppConfig, SubAppConfig

# Direct use of the settings is not recommended. Use the settings models.
settings = Dynaconf(
    envvar_prefix='SUBWTCH',
    settings_files=['settings.toml', '.secrets.toml'],
    # includes=["libs/**/settings.toml", "libs/**/.secrets.toml"],  # for testing purposes Need to enable after lib creating as external package
    environments=True,
    load_dotenv=False,
    merge_enabled=True
)

SETTINGS_ENV = settings.current_env

APP_CONFIG = AppConfig(**settings.get('SERVICE', {'APP_NAME': 'test'}))
SUB_APP_CONFIG = SubAppConfig(**settings.get('SERVICE', {'APP_NAME': 'test'}))

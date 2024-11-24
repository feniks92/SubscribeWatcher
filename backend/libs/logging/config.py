from copy import deepcopy
from typing import Literal

DEFAULT_LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    # loggers configuration mirrors gunicorn logger configuration from CONFIG_DEFAULTS
    # (see https://github.com/benoitc/gunicorn/blob/master/gunicorn/glogging.py),
    # otherwise "Unable to configure logger [root|gunicorn.error]" would be raised
    "root": {
        "handlers": ["default"],
        "level": "INFO",
        "propagate": True,
    },
    "loggers": {
        "aiokafka": {
            "handlers": ["default"],
            "level": "INFO",
        },
        "aiokafka.conn": {
            "handlers": ["default"],
            "level": "INFO",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "plaintext",
            "stream": "ext://sys.stdout",
        },
    },
    "formatters": {
        "plaintext": {
            "class": "libs.logging.CustomPlaintextFormatter",
            "format": "{levelname:<10}{message:<100}",
            "style": "{"
        },
        "json": {
            "class": "libs.logging.CustomJsonFormatter",
        }
    }
}

SQLALCHEMY_LOGGING_MIXIN: dict = {
    'loggers': {
        "sqlalchemy.engine": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        }
    }
}

UVICORN_GUNICORN_LOGGING_CONFIG_MIXIN: dict = {
    'loggers': {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
        "gunicorn.error": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "gunicorn.access": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "handlers": {
        "access": {
            "class": "logging.StreamHandler",
            "formatter": "access_debug",
            "stream": "ext://sys.stdout",
        },
    },
    "formatters": {
        "access_debug": {
            "class": "uvicorn.logging.AccessFormatter",
            "format": "%(levelprefix)s %(client_addr)s - %(request_line)s %(status_code)s",
        },
    }
}

LEVEL = Literal['debug', 'info', 'warning', 'error', 'critical']
FORMAT = Literal['text', 'json']


def _get_logging_config(config: dict,
                        level: LEVEL = "info",
                        fmt: FORMAT = "text",
                        is_log_database: bool = False) -> dict:
    if is_log_database:
        for key, value in SQLALCHEMY_LOGGING_MIXIN.items():
            config[key].update(value)
    if level != "info":
        level = level.upper()
        config['root']['level'] = level
        for logger in config['loggers']:
            config['loggers'][logger]['level'] = level

    if fmt == 'json':
        for handler in config['handlers']:
            config['handlers'][handler]['formatter'] = 'json'

    return config


def get_uvicorn_config(level: LEVEL = "info", fmt: FORMAT = "text", is_log_database: bool = False):
    config = deepcopy(DEFAULT_LOGGING_CONFIG)
    for key, value in UVICORN_GUNICORN_LOGGING_CONFIG_MIXIN.items():
        config[key].update(value)
    return _get_logging_config(config, level, fmt, is_log_database)


get_logging_config = get_uvicorn_config


def get_default_config(level: LEVEL = "info", fmt: FORMAT = "text", is_log_database: bool = False):
    config = deepcopy(DEFAULT_LOGGING_CONFIG)
    return _get_logging_config(config, level, fmt, is_log_database)


def init(level: LEVEL = "info", fmt: FORMAT = "text", is_log_database: bool = False):
    import logging.config
    logging.config.dictConfig(get_default_config(level, fmt, is_log_database))

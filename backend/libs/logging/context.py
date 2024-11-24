from contextvars import ContextVar
from enum import StrEnum
from typing import Any

from libs.config import settings
from libs.utils.crypt import hash_key

from .models import LogExtra


class LogContextKey(StrEnum):
    CONTEXT = 'service_context'
    MODEL = 'service_model'


_ctx = ContextVar('ctx')

encrypt_protected_values = settings.get('LOG', {}).get('ENCRYPT_PROTECTED_VALUES', False)


def get() -> dict[str, Any]:
    try:
        return _ctx.get()
    except LookupError:
        return {}


def set(key: str, value: Any):
    ctx = get()
    ctx[key] = value
    _ctx.set(ctx)


def set_service_log_model(value: type[LogExtra]):
    return set(LogContextKey.MODEL, value)


def get_service_log_model() -> type[LogExtra]:
    return get().get(LogContextKey.MODEL) or LogExtra


def set_service_context(value: dict):
    return set(LogContextKey.CONTEXT, value)


def get_service_context() -> dict:
    return get().get(LogContextKey.CONTEXT, {})

def set_protected(key: str, value: Any):
    if encrypt_protected_values and value:
        return set(f'{key}_hash', hash_key(str(value)))
    return set(key, value)
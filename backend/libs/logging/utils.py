import asyncio
from functools import wraps
from typing import Any, Iterable

from .logger import getLogger

log = getLogger('default-logger')


async def gather(*tasks, zip_with=None,
                 logger=log.exception,
                 msg='Failed to gather tasks',
                 extra_func=None,
                 ) -> Iterable[tuple[Any, Any]]:
    """
    Run provided tasks concurrenly and either yield the results or log exceptions
    """
    results = await asyncio.gather(*tasks, return_exceptions=True)
    if zip_with is not None:
        _iterator = zip(zip_with, results)
    else:
        _iterator = enumerate(results)

    for match, result in _iterator:
        if isinstance(result, BaseException):
            extra = extra_func(match) if extra_func else None
            logger(msg, extra=extra, exc_info=exc_info(result))
        else:
            yield match, result


@wraps(gather)
async def gather_all(*args, **kwargs) -> list[tuple[Any, Any]]:
    """
    Thin wrapper that ensures generator is exhausted and returns the list
    """
    return [item async for item in gather(*args, **kwargs)]


def exc_info(exception: BaseException):
    """
    Retrieve exception details when exception context is lost (e.g. in asyncio.gather, etc)
    """
    return type(exception), exception, exception.__traceback__

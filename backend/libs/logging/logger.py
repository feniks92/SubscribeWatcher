import logging
from typing import Any, Dict, Optional

import pydantic
from pythonjsonlogger import jsonlogger

from libs.config import settings

from .context import get_service_log_model

if pydantic.__version__.startswith('2.'):
    from .models import (LogBaseFile, LogExtra, LogExtraError, LogExtraInfo,
                         LogFile, LogOrigin)
else:
    from .models_v1 import (LogBaseFile, LogExtra, LogExtraError, LogExtraInfo,
                            LogFile, LogOrigin)


def getLogger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(settings.get("SERVICE.APP_NAME", "none")).getChild(name)


def getLoggerWithContext(log, context: dict) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(log, extra=context)


class CustomPlaintextFormatter(logging.Formatter):
    reserved_attrs = ['color_message', *jsonlogger.RESERVED_ATTRS]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model: type[LogExtra] = get_service_log_model()

    def get_record_extra(self, record) -> dict:
        extra_info = jsonlogger.merge_record_extra(record, {}, self.reserved_attrs)
        log_model = self.model(**extra_info)
        return log_model.dict(by_alias=True, exclude_none=True)

    def format(self, record):
        log_msg = super().format(record)
        if extra := self.get_record_extra(record):
            log_msg = f'{log_msg}{extra}'
        return log_msg


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    add_record_attrs = ['name', 'pathname', 'lineno', 'funcname', 'process']
    service_attrs = ('pathname', 'lineno', 'funcname', 'process')

    def __init__(self, *args, **kwargs):
        super().__init__(json_ensure_ascii=False, *args, **kwargs)
        self.model: type[LogExtra] = get_service_log_model()

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        log_extra = log_record.get('log', {})
        super().add_fields(log_extra, record, message_dict)
        log_info = LogExtraInfo.create_or_none(level=log_record.get('level', record.levelname).upper(),
                                               file=LogBaseFile(path=record.pathname),
                                               logger=record.name,
                                               origin=LogOrigin(
                                                   file=LogFile(line=str(record.lineno),
                                                                name=record.filename,
                                                                function=record.funcName,
                                                                module=record.module
                                                                ))
                                               )

        stack_trace = None
        if 'exc_info' in message_dict:
            stack_trace = message_dict.get('exc_info')
            log_extra.pop('exc_info', None)
        elif 'exc_info' in log_extra:
            stack_trace = log_extra.pop('exc_info')
        log_error = LogExtraError.create_or_none(message=record.exc_text, stack_trace=stack_trace)

        if 'error' in log_extra:
            log_extra.pop('error', None)
        log_model = self.model(log=log_info,
                               error=log_error,
                               **log_extra)
        log_record['log'] = log_model.dict(by_alias=True, exclude_none=True)


def set_kafka_log_level(level: str):
    level = logging.getLevelName(level.upper())
    logging.getLogger('aiokafka.conn').setLevel(level)
    logging.getLogger('kafka').setLevel(level)
    logging.getLogger('aiokafka').setLevel(level)


def set_service_log_level(level):
    level = logging.getLevelName(level.upper())
    logging.getLogger(settings.SERVICE.APP_NAME).setLevel(level)


def set_unleash_log_level(level):
    level = logging.getLevelName(level.upper())
    logging.getLogger('unleash').setLevel(level)
    logging.getLogger('urllib3').setLevel(level)
    logging.getLogger('apscheduler').setLevel(level)
    logging.getLogger('UnleashClient').setLevel(level)

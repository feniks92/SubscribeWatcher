import json
from typing import Any, Optional, Type, Union

import pydantic
from pydantic import BaseModel, ValidationError, parse_obj_as

if pydantic.__version__.startswith('2.'):
    from pydantic import TypeAdapter

from libs import logging
from libs.utils import crypt

SimpleTypes = Union[str, int, float]

logger = logging.getLogger('redis')


class BaseFieldSerializer:

    def encode(self, value: Any) -> SimpleTypes:
        raise NotImplementedError()

    def decode(self, value: Any) -> Any:
        raise NotImplementedError()


class DefaultSerializer(BaseFieldSerializer):

    def encode(self, value: Any) -> SimpleTypes:
        return value

    def decode(self, value: Any) -> Any:
        # TODO: Try to decode redis response over aioredis library. Check options `encoding` and `decode_responses`
        if isinstance(value, bytes):
            return value.decode(encoding='utf-8')
        return value


class StringSerializer(DefaultSerializer):

    def encode(self, value: Any) -> SimpleTypes:
        return str(super().encode(value))

    def decode(self, value: Any) -> Any:
        return str(super().decode(value)) if value else value


class JsonSerializer(BaseFieldSerializer):
    def encode(self, value: Any) -> SimpleTypes:
        return json.dumps(value) if value else value

    def decode(self, value: Any) -> Any:
        return json.loads(value) if value else value


class ModelSerializer(BaseFieldSerializer):
    def __init__(self, model: Type[BaseModel]):
        self._model = model

    def encode(self, value: Any) -> SimpleTypes:
        try:
            if pydantic.__version__.startswith('2.'):
                return value.model_dump_json(by_alias=True, exclude_none=True)
            else:
                return value.json(by_alias=True, ensure_ascii=False, exclude_none=True)
        except Exception:
            logger.exception('Error converting value to JSON')
            return ""

    def decode(self, value: Any) -> Any:
        if not value:
            return None
        try:
            if pydantic.__version__.startswith('2.'):
                return TypeAdapter(self._model).validate_python(json.loads(value))
            else:
                return parse_obj_as(self._model, json.loads(value))
        except ValidationError:
            logger.exception("Error parsing value from cache", extra={'type': self._model})
            return None


class ModelsListSerializer(BaseFieldSerializer):
    def __init__(self, model: Type[BaseModel]):
        self._model = model

    def encode(self, value: Any) -> SimpleTypes:
        try:
            if pydantic.__version__.startswith('2.'):
                return json.dumps([item.model_dump(by_alias=True) for item in value], default=str)
            else:
                return json.dumps([item.dict(by_alias=True) for item in value], default=str)
        except Exception:
            logger.exception('Error converting value to JSON')
            return ""

    def decode(self, value: Any) -> Any:
        try:
            if pydantic.__version__.startswith('2.'):
                _type_adapter = TypeAdapter(self._model)
                return [_type_adapter.validate_python(item) for item in json.loads(value)]
            else:
                return [parse_obj_as(self._model, item) for item in json.loads(value)]
        except ValidationError:
            logger.exception("Error parsing value from cache", extra={'type': list[self._model]})
            return None


class HashableSerializer(DefaultSerializer):
    def __init__(self, ancestor: BaseFieldSerializer):
        self._ancestor = ancestor

    def encode(self, value: Any) -> SimpleTypes:
        return value if value is None else crypt.hash_key(self._ancestor.encode(value))


class SecureHashableSerializer(DefaultSerializer):
    def __init__(self, ancestor: BaseFieldSerializer):
        self._ancestor = ancestor

    def encode(self, value: Any) -> SimpleTypes:
        return value if value is None else crypt.secure_hash_key(self._ancestor.encode(value))


class EncryptableSerializer(BaseFieldSerializer):
    def __init__(self, ancestor: BaseFieldSerializer):
        self._ancestor = ancestor

    def encode(self, value: Any) -> Optional[SimpleTypes]:
        return value if value is None else crypt.encrypt(self._ancestor.encode(value))

    def decode(self, value: Any) -> Any:
        return value if value is None else self._ancestor.decode(crypt.decrypt(value))


class RedisRecordSerializer:

    def __init__(self,
                 key_serializer: BaseFieldSerializer,
                 value_serializer: BaseFieldSerializer):
        self.key_serializer = key_serializer
        self.value_serializer = value_serializer

    def encode_key(self, key: str) -> str:
        return self.key_serializer.encode(key)

    def encode(self, key: str, value: Any = None) -> tuple[str, Optional[str]]:
        return (self.encode_key(key),
                value if value is None else self.value_serializer.encode(value))

    def decode(self, value: Optional[str]) -> Any:
        return self.value_serializer.decode(value)

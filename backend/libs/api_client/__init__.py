from dynaconf.utils.boxing import DynaBox

from .api_client import ApiClientInterface
from .api_client_impl import ApiClient


def create_api_client(config: DynaBox) -> ApiClientInterface:
    return ApiClient.create(config)

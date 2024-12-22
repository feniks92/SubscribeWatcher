from libs.api_client.api_client_impl import ApiClient  # noqa
from libs.api_client.api_service import ApiService, Authorization, BaseRequest  # noqa


# TODO пока нет ясности наличия общего флоу и методов у всех фин интеграций. Оставил как зедал на будущее
class BasePaymentSystemAPI(ApiService):
    pass

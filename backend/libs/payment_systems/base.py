from libs.api_client.api_client_impl import ApiClient  # noqa
from libs.api_client.api_service import ApiService, Authorization, BaseRequest  # noqa


# TODO пока нет ясности наличия общего флоу и методов у всех фин интеграций. Оставил как задел на будущее
class BasePaymentSystemAPI(ApiService):
    async def create_invoice(self):
        raise NotImplementedError

    async def check_invoice(self):
        raise NotImplementedError

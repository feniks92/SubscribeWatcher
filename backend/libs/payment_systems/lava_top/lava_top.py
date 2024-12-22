from libs.api_client.api_client import T, Type
from libs.api_client.api_service import ApiService
from libs.api_client.exceptions import ApiException, ExpectedClientError, TimeoutClientError, UnexpectedResponse
from libs.config import settings

from .api_client import LavaTopApiClient
from .models import LavaTopProductsResponse, Offer, Invoice


ACCPETABLE_PAYMENT_STATUSES = ('completed', 'subscription-active')

class LavaTopApi(ApiService):
    client: LavaTopApiClient.create(settings.LAVA_TOP)

    def __init__(self, cookies: dict | None = None):
        super().__init__()

        self.headers = {
            "X-Api-Key": settings.LAVA_TOP.API_KEY
        }

        self.cookies = cookies or {}

    async def _request(self, method: str = "GET", type_: Type[T] = None, url: str | None = None,
                       raise_exception: bool = True, return_exception: bool = False,
                       **kwargs) -> T | Exception | None:
        self.headers.update(kwargs.pop('headers', {}))
        self.cookies.update(kwargs.pop('cookies', {}))
        return await super()._request(method=method, type_=type_, url=url,
                                      raise_exception=raise_exception,
                                      return_exception=return_exception,
                                      headers=self.headers,
                                      cookies=self.cookies,
                                      **kwargs)

    async def get_products(self):
        try:
            return await super().get_response(
                type_=LavaTopProductsResponse
            )
        # TODO доделать эксепшены
        except TimeoutClientError as exc:
            pass

    async def create_invoice(self, offer: Offer, email: str) -> Invoice:
        pass

    async def check_payment_status(self, payment_id) -> bool:
        pass

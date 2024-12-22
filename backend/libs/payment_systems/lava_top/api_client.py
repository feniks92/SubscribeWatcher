from libs.api_client.api_client_impl import ApiClient
from libs.api_client.models import ApiIntegrationSettings


class LavaTopApiClient(ApiClient):
    config: ApiIntegrationSettings

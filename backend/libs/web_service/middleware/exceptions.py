import pydantic
from fastapi.exceptions import RequestValidationError


class HeaderValidationError(RequestValidationError):

    def __init__(self, exc):
        super().__init__(errors=[exc])

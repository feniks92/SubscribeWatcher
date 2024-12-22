import json
from typing import Any, Dict, Optional

from httpx import Headers, Request, Response

MAX_CONTENT = 200


class ApiException(Exception):
    _title = 'Base api exception'

    def __str__(self) -> str:
        return self._title


class UnexpectedResponse(ApiException):
    _title = 'Unexpected Response'

    def __init__(self, status_code: Optional[int], reason_phrase: str, content: bytes, headers: Headers):
        self.status_code = status_code
        self.reason_phrase = reason_phrase
        self.content = content
        self.headers = headers

    @classmethod
    def for_request(cls, request: Request) -> "ApiException":
        return cls(
            status_code=None,
            reason_phrase=request.url,
            content=request.content,
            headers=request.headers,
        )

    @classmethod
    def for_response(cls, response: Response) -> "ApiException":
        return cls(
            status_code=response.status_code,
            reason_phrase=response.reason_phrase,
            content=response.content,
            headers=response.headers,
        )

    def __str__(self) -> str:
        status_code_str = f"{self.status_code}" if self.status_code is not None else ""
        if self.reason_phrase == "" and self.status_code is not None:
            reason_phrase_str = "(Unrecognized Status Code)"
        else:
            reason_phrase_str = f"({self.reason_phrase})"
        status_str = f"{status_code_str} {reason_phrase_str}".strip()
        short_content = self.content if len(self.content) <= MAX_CONTENT else self.content[: MAX_CONTENT - 3] + b" ..."
        raw_content_str = f"Raw response content:\n{short_content.decode('utf-8')!r}"
        return f"{self._title}: {status_str}\n{raw_content_str}"

    def structured(self) -> Dict[str, Any]:
        return json.loads(self.content)


class ExpectedClientError(UnexpectedResponse):
    _title = 'Expected Client Error'
    """
    Contains same information as UnexpectedResponse
    but should be logged with level not higher than 'warning'.
    """


class ServiceTemporaryDisabled(ApiException):
    _title = 'Service temporary disabled'


class ResponseHandlingException(ApiException):
    def __init__(self, source: BaseException):
        self.source = source
        super().__init__(str(source))


class ResponseValidationException(ResponseHandlingException):
    ...


class TimeoutClientError(ExpectedClientError):
    _title = 'Timeout Client Error'


class BadRequestException(ApiException):
    ...


class RetryAttemptsOutError(TimeoutClientError):
    _title = 'Max request attempts'

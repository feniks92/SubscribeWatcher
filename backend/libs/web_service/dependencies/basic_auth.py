import secrets
from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.requests import Request

from libs.config import settings
from libs.web_service.middleware.rfc7807 import Problem


class BasicAuthSecurity(HTTPBasic):
    _username: Optional[str] = settings.SECURE.BASIC_AUTH.USERNAME
    _password: Optional[str] = settings.SECURE.BASIC_AUTH.PASSWORD

    @staticmethod
    def is_correct(actual: Optional[str], expects: Optional[str]) -> bool:
        return secrets.compare_digest(actual.encode('utf-8'),
                                      expects.encode('utf-8'))

    async def __call__(  # type: ignore
            self, request: Request
    ) -> Optional[HTTPBasicCredentials]:
        if settings.SECURE.STATE:
            credentials = await super().__call__(request)
            if credentials and (self.is_correct(credentials.username, self._username) and
                                self.is_correct(credentials.password, self._password)):
                return credentials

            raise Problem(status=404)

        return


basic_auth_security = Depends(BasicAuthSecurity(auto_error=False))

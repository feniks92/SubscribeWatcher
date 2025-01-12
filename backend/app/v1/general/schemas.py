from typing import Optional

from pydantic import Field

from libs.shared import AuthorizeItem


class AuthorizeResponse(AuthorizeItem):
    rq_id: Optional[str] = Field(None, description='Идентификатор запроса',
                                 examples=['698c6fc1-b284-4f4b-b9a6-f317b1bf0811'], alias='rqId')

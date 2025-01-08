from pydantic import BaseModel, Field

from datetime import datetime
from typing import Optional

from app.v1.general.schemas import TariffItem


class SubscriptionInfoResponse(BaseModel):
    rq_id: Optional[str] = Field(None, description='Идентификатор запроса',
                                 examples=['698c6fc1-b284-4f4b-b9a6-f317b1bf0811'], alias='rqId')
    tariff: TariffItem = Field(..., alias='tariffs')
    subscription_end: Optional[datetime] = Field(None, alias='subscription_end')

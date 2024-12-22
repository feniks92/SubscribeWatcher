from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.background import BackgroundTasks
from starlette.requests import Request

from libs import logging
from libs.database.sql_alchemy import pass_db_session, Session

from .handler import AuthorizeHandler, ChannelHandler
from .schemas import ChannelResponse, AuthorizeResponse, ParticipantsInfo, SubscriptionInfoResponse

router = APIRouter(
    prefix="/subscribe",
    tags=["subscribe_watcher"],
    responses={404: {"description": "Not found"},
               422: {"description": "Request validation error"}},
)


@router.post(path="/authorize", response_model=AuthorizeResponse)
async def authorize(
        request: Request,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo),

) -> AuthorizeResponse:
    handler = AuthorizeHandler(session=db_session,
                               participants=participants)

    return AuthorizeResponse(roles= await handler.handle(bg_tasks=background_tasks))



@router.get("/channels", response_model=ChannelResponse)
async def channels_list(
        request: Request,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo),
) -> list[ChannelResponse]:
    handler = ChannelHandler(session=db_session,
                             participants=participants)

    return await handler.handle(bg_tasks=background_tasks)


#  Ручка для получения текущих подписок пользователя
@router.get("/subscription", response_model=SubscriptionInfoResponse)
async def channels_list(
        request: Request,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo),
) -> SubscriptionInfoResponse:
    handler = SubscriptionHandler(session=db_session,
                             participants=participants)

    return await handler.handle(bg_tasks=background_tasks)
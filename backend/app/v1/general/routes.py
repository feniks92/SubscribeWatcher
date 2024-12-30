from fastapi import APIRouter, Depends
from starlette.background import BackgroundTasks
from starlette.requests import Request

from libs import logging
from libs.database.sql_alchemy import pass_db_session, Session
from libs.dependencies import ParticipantsInfo

from .handler import AuthorizeHandler
from .schemas import AuthorizeResponse

log = logging.getLogger('watcher_handler')

router = APIRouter(
    prefix="",
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

    user_type, bot_type = await handler.handle(bg_tasks=background_tasks)
    return AuthorizeResponse(user_type=user_type, bot_type=bot_type)
from starlette.requests import Request
from starlette.responses import JSONResponse

from .base import BaseHTTPMiddleware


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            if response.status_code == 500:
                return JSONResponse({"title": "Internal Server Error"}, status_code=500)
            return response
        except Exception:
            return JSONResponse({"title": "Internal Server Error"}, status_code=500)

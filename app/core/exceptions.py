from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.schemas.common import ErrorResponse


class AppException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(_, exc: AppException) -> JSONResponse:
        payload = ErrorResponse(detail=exc.message).model_dump()
        return JSONResponse(status_code=exc.status_code, content=payload)

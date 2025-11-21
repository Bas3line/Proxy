from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger
from app.core.exceptions import ProxyException


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except ProxyException as e:
            logger.warning(f"Proxy exception: {e.detail} [Status: {e.status_code}]")
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": e.detail,
                    "status_code": e.status_code,
                    "path": str(request.url.path)
                }
            )
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "status_code": 500,
                    "path": str(request.url.path)
                }
            )

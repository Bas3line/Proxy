import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        request_id = request.headers.get("X-Request-ID", f"{int(time.time() * 1000)}")

        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"[Client: {request.client.host}] [ID: {request_id}]"
        )

        response = await call_next(request)

        process_time = time.time() - start_time

        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"[Status: {response.status_code}] [Time: {process_time:.3f}s] [ID: {request_id}]"
        )

        return response

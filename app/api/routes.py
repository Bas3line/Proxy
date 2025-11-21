from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.proxy import proxy_service
from app.core.config import get_settings
from app.core.logging import logger


router = APIRouter()


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy_all(request: Request, path: str = ""):
    return await proxy_service.proxy_request(request, path)


@router.get("/", include_in_schema=False)
async def proxy_root(request: Request):
    return await proxy_service.proxy_request(request, "")


health_router = APIRouter(prefix="/api", tags=["Health"])


@health_router.get("/health")
async def health_check():
    settings = get_settings()

    status = {
        "status": "healthy",
        "target_url": settings.target_url,
        "timeout": settings.request_timeout,
        "ssl_verify": settings.ssl_verify
    }

    logger.debug("Health check called")

    return JSONResponse(content=status, status_code=200)


@health_router.get("/ping")
async def ping():
    return {"message": "pong"}

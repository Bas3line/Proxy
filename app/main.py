from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging import logger
from app.services.proxy import proxy_service
from app.middleware.request_logging import RequestLoggingMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.api.routes import router, health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Starting AI Proxy Service")
    logger.info(f"Target URL: {settings.target_url}")
    logger.info(f"Timeout: {settings.request_timeout}s")

    await proxy_service.initialize()
    logger.info("Proxy service initialized")

    yield

    logger.info("Shutting down AI Proxy Service")
    await proxy_service.close()
    logger.info("Proxy service closed")


def create_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="AI Proxy Service",
        description="Reverse proxy for ai.megallm.io",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan
    )

    if settings.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=settings.cors_methods,
            allow_headers=settings.cors_headers,
        )

    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(health_router)
    app.include_router(router)

    return app


app = create_application()

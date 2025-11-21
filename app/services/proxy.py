import httpx
from typing import Dict, Any, Optional
from urllib.parse import urljoin, urlencode
from fastapi import Request
from fastapi.responses import StreamingResponse
from app.core.config import get_settings
from app.core.logging import logger
from app.core.exceptions import TargetServerException, TimeoutException


class ProxyService:
    EXCLUDED_HEADERS = {
        "host", "connection", "keep-alive", "proxy-authenticate",
        "proxy-authorization", "te", "trailers", "transfer-encoding",
        "upgrade", "content-length", "content-encoding"
    }

    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[httpx.AsyncClient] = None

    async def initialize(self):
        timeout = httpx.Timeout(
            connect=10.0,
            read=self.settings.request_timeout,
            write=self.settings.request_timeout,
            pool=10.0
        )

        limits = httpx.Limits(
            max_keepalive_connections=20,
            max_connections=100
        )

        self.client = httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            follow_redirects=False,
            verify=self.settings.ssl_verify,
            http2=True
        )

    async def close(self):
        if self.client:
            await self.client.aclose()

    def _build_target_url(self, path: str, query_params: Dict[str, Any]) -> str:
        base_url = self.settings.target_url.rstrip("/")
        path = path.lstrip("/")

        url = f"{base_url}/{path}" if path else base_url

        if query_params:
            query_string = urlencode(query_params, doseq=True)
            url = f"{url}?{query_string}"

        return url

    def _prepare_headers(self, request: Request) -> Dict[str, str]:
        headers = {}

        for key, value in request.headers.items():
            if key.lower() not in self.EXCLUDED_HEADERS:
                headers[key] = value

        headers["X-Forwarded-For"] = request.client.host
        headers["X-Forwarded-Proto"] = request.url.scheme
        headers["X-Forwarded-Host"] = request.headers.get("host", "")
        headers["X-Real-IP"] = request.client.host

        if "user-agent" not in headers:
            headers["User-Agent"] = "AI-Proxy-Service/1.0"

        return headers

    async def _forward_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: bytes
    ) -> httpx.Response:
        try:
            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                content=body if body else None
            )
            return response
        except httpx.TimeoutException as e:
            logger.error(f"Timeout error for {method} {url}: {str(e)}")
            raise TimeoutException(detail=f"Request timed out after {self.settings.request_timeout}s")
        except httpx.ConnectError as e:
            logger.error(f"Connection error for {method} {url}: {str(e)}")
            raise TargetServerException(detail="Unable to connect to target server")
        except httpx.RequestError as e:
            logger.error(f"Request error for {method} {url}: {str(e)}")
            raise TargetServerException(detail=f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error for {method} {url}: {str(e)}")
            raise TargetServerException(detail="Internal proxy error")

    def _prepare_response_headers(self, response: httpx.Response) -> Dict[str, str]:
        headers = {}

        for key, value in response.headers.items():
            if key.lower() not in self.EXCLUDED_HEADERS:
                headers[key] = value

        headers["X-Proxy-By"] = "AI-Proxy-Service"

        return headers

    async def _stream_response(self, response: httpx.Response):
        try:
            async for chunk in response.aiter_bytes(chunk_size=self.settings.proxy_buffer_size):
                yield chunk
        except Exception as e:
            logger.error(f"Error streaming response: {str(e)}")
            raise
        finally:
            await response.aclose()

    async def proxy_request(self, request: Request, path: str = "") -> StreamingResponse:
        query_params = dict(request.query_params)
        target_url = self._build_target_url(path, query_params)
        headers = self._prepare_headers(request)
        body = await request.body()

        logger.info(f"Proxying {request.method} {target_url}")

        response = await self._forward_request(
            method=request.method,
            url=target_url,
            headers=headers,
            body=body
        )

        response_headers = self._prepare_response_headers(response)

        logger.info(f"Response {response.status_code} from {target_url}")

        return StreamingResponse(
            content=self._stream_response(response),
            status_code=response.status_code,
            headers=response_headers,
            media_type=response.headers.get("content-type")
        )


proxy_service = ProxyService()

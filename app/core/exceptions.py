from fastapi import HTTPException, status


class ProxyException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class TargetServerException(ProxyException):
    def __init__(self, detail: str = "Failed to connect to target server"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)


class TimeoutException(ProxyException):
    def __init__(self, detail: str = "Request to target server timed out"):
        super().__init__(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=detail)


class InvalidRequestException(ProxyException):
    def __init__(self, detail: str = "Invalid request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

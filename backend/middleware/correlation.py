from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import uuid


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        cid = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.correlation_id = cid
        resp: Response = await call_next(request)
        resp.headers["X-Request-ID"] = cid
        return resp

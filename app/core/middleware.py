import os
import uuid
from fastapi import Request
from app.core.auth import auth_service


def _allowed_cors_origins() -> set[str]:
    origins = {
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081",
    }
    frontend_urls = os.getenv("FRONTEND_URLS", "").split(",")
    origins.update({url.strip() for url in frontend_urls if url.strip()})
    return origins


def _cors_headers_for_request(request: Request) -> dict[str, str]:
    origin = request.headers.get("origin")
    if not origin:
        return {}

    if origin not in _allowed_cors_origins():
        return {}

    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Vary": "Origin",
    }

async def correlation_id_middleware(request: Request, call_next):
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id

    response = await call_next(request)
    response.headers["X-Correlation-Id"] = correlation_id
    return response


async def auth_middleware(request: Request, call_next):
    require_auth = os.getenv("REQUIRE_AUTH", "true").lower() == "true"

    if not require_auth:
        return await call_next(request)

    path = request.url.path
    # Always allow CORS preflight OPTIONS requests to pass through without auth
    # The CORS middleware will handle the actual CORS headers
    if request.method == "OPTIONS":
        return await call_next(request)

    if path.startswith("/api/v1/auth") or path in {"/", "/health", "/version"}:
        return await call_next(request)

    if path.startswith("/docs") or path.startswith("/openapi") or path.startswith("/redoc"):
        return await call_next(request)

    allow_query_token = os.getenv("ALLOW_QUERY_ACCESS_TOKEN", "false").lower() == "true"
    supports_query_token = (
        path.startswith("/api/v1/ai/stream/")
        or path.startswith("/api/v1/realtime/transactions")
    )

    # Keep query-token auth behind an explicit flag for legacy clients.
    if allow_query_token and supports_query_token:
        query_token = request.query_params.get("access_token", "").strip()
        if query_token:
            try:
                request.state.user = await auth_service.get_current_user(query_token)
                return await call_next(request)
            except Exception:
                return await _unauthorized(request)

    auth_header = request.headers.get("Authorization", "")
    bearer_token = auth_header.replace("Bearer ", "", 1).strip() if auth_header.startswith("Bearer ") else ""
    cookie_token = request.cookies.get("access_token", "").strip()
    token = bearer_token or cookie_token

    if not token:
        return await _unauthorized(request)

    try:
        request.state.user = await auth_service.get_current_user(token)
    except Exception:
        return await _unauthorized(request)

    return await call_next(request)


async def _unauthorized(request: Request):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=401,
        content={"detail": "Unauthorized"},
        headers=_cors_headers_for_request(request),
    )

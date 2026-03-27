import os
import uuid
from fastapi import Request
from app.core.auth import auth_service

async def correlation_id_middleware(request: Request, call_next):
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id

    response = await call_next(request)
    response.headers["X-Correlation-Id"] = correlation_id
    return response


async def auth_middleware(request: Request, call_next):
    require_auth = os.getenv("REQUIRE_AUTH")
    if require_auth is None:
        require_auth = "true" if os.getenv("ENVIRONMENT", "local") == "production" else "false"

    if require_auth.lower() != "true":
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

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return await _unauthorized()

    token = auth_header.replace("Bearer ", "", 1).strip()
    try:
        request.state.user = await auth_service.get_current_user(token)
    except Exception:
        return await _unauthorized()

    return await call_next(request)


async def _unauthorized():
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=401,
        content={"detail": "Unauthorized"},
    )

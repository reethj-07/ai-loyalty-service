import os
from fastapi import Header, HTTPException, Request


def get_tenant_id(x_tenant_id: str = Header(...)):
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header missing")
    return x_tenant_id


def _tenant_from_user_context(request: Request) -> str | None:
    user = getattr(request.state, "user", None)
    if not isinstance(user, dict):
        return None

    metadata = user.get("user_metadata") or user.get("metadata") or {}
    if not isinstance(metadata, dict):
        metadata = {}

    for key in ("tenant_id", "tenantId", "workspace_id", "workspaceId", "org_id", "organization_id"):
        value = metadata.get(key) or user.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return None


def resolve_tenant_id(request: Request, x_tenant_id: str | None = Header(None)):
    tenant_mode = os.getenv("TENANT_MODE")
    if tenant_mode is None:
        tenant_mode = "true" if os.getenv("ENVIRONMENT", "local") == "production" else "false"

    tenant_id = (x_tenant_id or "").strip() or _tenant_from_user_context(request)

    if not tenant_id:
        default_tenant = os.getenv("DEFAULT_TENANT_ID", "").strip()
        tenant_id = default_tenant or None

    if tenant_mode.lower() == "true" and not tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header missing")

    return tenant_id

import os
from fastapi import Header, HTTPException


def get_tenant_id(x_tenant_id: str = Header(...)):
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header missing")
    return x_tenant_id


def resolve_tenant_id(x_tenant_id: str | None = Header(None)):
    tenant_mode = os.getenv("TENANT_MODE")
    if tenant_mode is None:
        tenant_mode = "true" if os.getenv("ENVIRONMENT", "local") == "production" else "false"

    if tenant_mode.lower() == "true" and not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header missing")
    return x_tenant_id

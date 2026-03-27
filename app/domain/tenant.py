from dataclasses import dataclass

@dataclass(frozen=True)
class TenantContext:
    tenant_id: str
    brand_id: str
    industry: str

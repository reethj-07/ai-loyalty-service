# services/tenant_resolver.py
class TenantResolver:
    async def resolve(self, tenant_id: str, brand_id: str) -> dict:
        return {
            "tenant_id": tenant_id,
            "brand_id": brand_id,
            "industry": "retail"
        }

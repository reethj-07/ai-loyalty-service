const TENANT_STORAGE_KEY = "tenant_id";

const TENANT_CLAIM_KEYS = ["tenant_id", "tenantId", "workspace_id", "workspaceId", "org_id", "organization_id"];

function readEnvDefaultTenantId(): string | null {
  const configured = (import.meta.env.VITE_DEFAULT_TENANT_ID as string | undefined)?.trim();
  return configured ? configured : null;
}

function readTenantFromUser(user: any): string | null {
  if (!user || typeof user !== "object") return null;

  const metadata = {
    ...(user.metadata && typeof user.metadata === "object" ? user.metadata : {}),
    ...(user.user_metadata && typeof user.user_metadata === "object" ? user.user_metadata : {}),
  } as Record<string, unknown>;

  for (const key of TENANT_CLAIM_KEYS) {
    const value = metadata[key] ?? (user as Record<string, unknown>)[key];
    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
  }

  return null;
}

export function getTenantId(): string | null {
  const stored = localStorage.getItem(TENANT_STORAGE_KEY)?.trim();
  if (stored) {
    return stored;
  }

  const fallback = readEnvDefaultTenantId();
  if (fallback) {
    localStorage.setItem(TENANT_STORAGE_KEY, fallback);
    return fallback;
  }

  return null;
}

export function setTenantId(tenantId: string | null | undefined) {
  const normalized = tenantId?.trim();
  if (!normalized) return;
  localStorage.setItem(TENANT_STORAGE_KEY, normalized);
}

export function syncTenantFromUser(user: any) {
  const userTenant = readTenantFromUser(user);
  if (userTenant) {
    setTenantId(userTenant);
    return userTenant;
  }

  return getTenantId();
}

export function clearTenantId() {
  localStorage.removeItem(TENANT_STORAGE_KEY);
}

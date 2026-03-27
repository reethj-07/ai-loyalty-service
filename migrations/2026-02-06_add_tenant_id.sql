-- Migration: Add tenant_id columns and indexes for multi-tenant scoping
-- Safe to run multiple times due to IF NOT EXISTS guards.

begin;

alter table if exists members
  add column if not exists tenant_id uuid;

alter table if exists transactions
  add column if not exists tenant_id uuid;

alter table if exists campaigns
  add column if not exists tenant_id uuid;

create index if not exists idx_members_tenant on members(tenant_id);
create index if not exists idx_transactions_tenant on transactions(tenant_id);
create index if not exists idx_campaigns_tenant on campaigns(tenant_id);

commit;

-- Reminder:
-- Update RLS policies to enforce tenant_id scoping once auth is enabled.
-- See DATABASE_SETUP.md for example policies.

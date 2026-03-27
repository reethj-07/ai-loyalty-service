-- Migration: Replace RLS policies with tenant-scoped rules
-- WARNING: This enforces tenant_id = auth.uid() for all access.
-- Adjust if you need shared data or a different tenant model.

begin;

alter table if exists members enable row level security;
alter table if exists transactions enable row level security;
alter table if exists campaigns enable row level security;

-- Members
 drop policy if exists members_select on members;
 drop policy if exists members_insert on members;
 drop policy if exists members_update on members;
 drop policy if exists members_delete on members;

create policy members_select on members
  for select using (tenant_id = auth.uid());

create policy members_insert on members
  for insert with check (tenant_id = auth.uid());

create policy members_update on members
  for update using (tenant_id = auth.uid());

create policy members_delete on members
  for delete using (tenant_id = auth.uid());

-- Transactions
 drop policy if exists transactions_select on transactions;
 drop policy if exists transactions_insert on transactions;
 drop policy if exists transactions_update on transactions;
 drop policy if exists transactions_delete on transactions;

create policy transactions_select on transactions
  for select using (tenant_id = auth.uid());

create policy transactions_insert on transactions
  for insert with check (tenant_id = auth.uid());

create policy transactions_update on transactions
  for update using (tenant_id = auth.uid());

create policy transactions_delete on transactions
  for delete using (tenant_id = auth.uid());

-- Campaigns
 drop policy if exists campaigns_select on campaigns;
 drop policy if exists campaigns_insert on campaigns;
 drop policy if exists campaigns_update on campaigns;
 drop policy if exists campaigns_delete on campaigns;

create policy campaigns_select on campaigns
  for select using (tenant_id = auth.uid());

create policy campaigns_insert on campaigns
  for insert with check (tenant_id = auth.uid());

create policy campaigns_update on campaigns
  for update using (tenant_id = auth.uid());

create policy campaigns_delete on campaigns
  for delete using (tenant_id = auth.uid());

commit;

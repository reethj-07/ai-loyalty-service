# 🗄️ Database Setup Guide

This guide explains how to set up Supabase for the AI Loyalty Service.

---

## Prerequisites

- Supabase account at https://supabase.com
- A new Supabase project
- Access to the Supabase SQL Editor
- A local `.env` file

---

## Step 1: Create Supabase Project

1. Create a project at https://supabase.com
2. Open **Project Settings** → **API**
3. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** → `SUPABASE_ANON_KEY`
   - **service_role secret** → `SUPABASE_SERVICE_KEY`

Update `.env`:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
```

---

## Step 2: Run Alembic Migrations (Recommended)

Run migrations from the project root:

```bash
alembic upgrade head
```

This applies the latest schema safely and reproducibly. Use manual SQL only for troubleshooting or ad-hoc environments.

## Step 3: Manual SQL Reference (Optional)

Open **SQL Editor** and run the SQL below if Alembic is not available.

### 2.1 Enable UUID extension

```sql
create extension if not exists "pgcrypto";
```

### 2.2 Members

```sql
create table if not exists members (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid,
  first_name text not null,
  last_name text not null,
  email text unique,
  mobile text unique,
  tier text default 'Bronze',
  points_balance numeric default 0,
  status text default 'active',
  created_at timestamptz default now()
);

create index if not exists idx_members_tenant on members(tenant_id);
create index if not exists idx_members_tier on members(tier);
create index if not exists idx_members_status on members(status);
```

### 2.3 Transactions

```sql
create table if not exists transactions (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid,
  member_id uuid not null references members(id) on delete cascade,
  amount numeric not null,
  merchant text,
  type text default 'purchase',
  category text default 'general',
  channel text,
  currency text default 'USD',
  transaction_date timestamptz default now(),
  created_at timestamptz default now()
);

create index if not exists idx_transactions_tenant on transactions(tenant_id);
create index if not exists idx_transactions_member on transactions(member_id);
create index if not exists idx_transactions_date on transactions(transaction_date);
```

### 2.4 Campaigns

```sql
create table if not exists campaigns (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid,
  name text not null,
  description text,
  campaign_type text,
  objective text,
  channel text,
  status text default 'draft',
  start_date date,
  end_date date,
  estimated_roi numeric,
  estimated_cost numeric,
  estimated_revenue numeric,
  created_by text,
  created_at timestamptz default now()
);

create index if not exists idx_campaigns_tenant on campaigns(tenant_id);
create index if not exists idx_campaigns_status on campaigns(status);
create index if not exists idx_campaigns_created on campaigns(created_at);
```

---

## Step 3: Row Level Security (RLS)

Enable RLS and apply basic policies. Adjust to your auth model.

```sql
alter table members enable row level security;
alter table transactions enable row level security;
alter table campaigns enable row level security;

create policy "members_select" on members
  for select using (tenant_id = auth.uid() or tenant_id is null);

create policy "members_insert" on members
  for insert with check (tenant_id = auth.uid() or tenant_id is null);

create policy "transactions_select" on transactions
  for select using (tenant_id = auth.uid() or tenant_id is null);

create policy "transactions_insert" on transactions
  for insert with check (tenant_id = auth.uid() or tenant_id is null);

create policy "campaigns_select" on campaigns
  for select using (tenant_id = auth.uid() or tenant_id is null);

create policy "campaigns_insert" on campaigns
  for insert with check (tenant_id = auth.uid() or tenant_id is null);
```

---

## Step 4: Seed Test Data (Optional)

The seed script uses the service key to bypass RLS:

```bash
python seed_database.py
```

---

## Step 5: Verify Connection

```bash
python -c "from app.core.supabase_client import get_supabase; print(get_supabase().table('members').select('id').limit(1).execute())"
```

---

## Environment Variables

Required:

```bash
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...
```

Optional:

```bash
REDIS_URL=redis://localhost:6379
AUTO_APPROVE_CAMPAIGNS=false
AUTO_EXECUTE_CAMPAIGNS=false
REQUIRE_AUTH=true
TENANT_MODE=true
DEFAULT_TENANT_ID=
EVENT_QUEUE_KEY=event_queue
```

---

## Support

- Supabase Docs: https://supabase.com/docs
- Service config: [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md)

---

**Last Updated:** February 6, 2026

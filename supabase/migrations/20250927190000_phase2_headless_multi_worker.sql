-- Phase 2: Supabase schema for headless chart service multi-worker coordination
-- Adds worker tracking, job leasing, and webhook event management for
-- distributed processing and reliable webhook delivery.

-- Ensure required extensions are available
create extension if not exists pgcrypto;

-- Use dedicated schema for headless service artifacts
create schema if not exists headless;
set search_path to headless, public;

-- Create or ensure headless_jobs table exists (Phase 1 table)
create table if not exists headless_jobs (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  timeframe text not null,
  commands jsonb not null default '[]'::jsonb,
  priority integer not null default 0,
  status text not null check (status in (
    'pending', 'in_progress', 'completed', 'failed', 'cancelled'
  )) default 'pending',
  browser_context_id text,
  result jsonb,
  error text,
  created_at timestamptz not null default timezone('utc', now()),
  started_at timestamptz,
  completed_at timestamptz,
  updated_at timestamptz not null default timezone('utc', now()),
  webhook_url text,
  webhook_secret text,
  metadata jsonb not null default '{}'::jsonb
);

-- Create function for updated_at if not exists
create or replace function headless_touch_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = timezone('utc', now());
  return new;
end;
$$;

-- Worker instances table for tracking active workers
create table if not exists headless_workers (
  id text primary key,
  hostname text not null,
  capabilities jsonb not null default '{}'::jsonb,
  max_concurrent integer not null default 3,
  active_jobs integer not null default 0,
  status text not null check (status in (
    'starting', 'active', 'idle', 'draining', 'stopped'
  )) default 'starting',
  last_heartbeat timestamptz not null default timezone('utc', now()),
  started_at timestamptz not null default timezone('utc', now()),
  stopped_at timestamptz,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create index if not exists idx_headless_workers_status_heartbeat
  on headless_workers (status, last_heartbeat desc);

create index if not exists idx_headless_workers_hostname
  on headless_workers (hostname);

-- Job leases table for distributed job processing
create table if not exists headless_job_leases (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references headless_jobs(id) on delete cascade,
  worker_id text not null references headless_workers(id) on delete cascade,
  lease_token text not null unique,
  lease_expires_at timestamptz not null,
  acquired_at timestamptz not null default timezone('utc', now()),
  renewed_at timestamptz not null default timezone('utc', now()),
  renewed_count integer not null default 0,
  released_at timestamptz,
  status text not null check (status in (
    'active', 'expired', 'released', 'failed'
  )) default 'active',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now()),
  
  -- Ensure one active lease per job
  constraint unique_active_job_lease 
    exclude (job_id with =) where (status = 'active')
);

create index if not exists idx_headless_job_leases_job_worker
  on headless_job_leases (job_id, worker_id);

create index if not exists idx_headless_job_leases_status_expires
  on headless_job_leases (status, lease_expires_at);

create index if not exists idx_headless_job_leases_token
  on headless_job_leases (lease_token);

-- Webhook events table for tracking delivery attempts
create table if not exists headless_webhook_events (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references headless_jobs(id) on delete cascade,
  event_type text not null check (event_type in (
    'job_queued', 'job_started', 'job_completed', 'job_failed', 
    'job_retried', 'job_cancelled'
  )),
  webhook_url text not null,
  payload jsonb not null,
  status text not null check (status in (
    'pending', 'sending', 'delivered', 'failed', 'cancelled'
  )) default 'pending',
  attempts integer not null default 0,
  max_attempts integer not null default 3,
  next_attempt_at timestamptz not null default timezone('utc', now()),
  last_attempt_at timestamptz,
  response_status integer,
  response_body text,
  error_message text,
  delivered_at timestamptz,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create index if not exists idx_headless_webhook_events_job_type
  on headless_webhook_events (job_id, event_type);

create index if not exists idx_headless_webhook_events_status_next_attempt
  on headless_webhook_events (status, next_attempt_at) 
  where status in ('pending', 'failed');

create index if not exists idx_headless_webhook_events_created_at
  on headless_webhook_events (created_at desc);

-- Trigger to keep updated_at in sync for new tables
drop trigger if exists trg_headless_workers_touch_updated on headless_workers;
create trigger trg_headless_workers_touch_updated
  before update on headless_workers
  for each row
  execute function headless_touch_updated_at();

drop trigger if exists trg_headless_job_leases_touch_updated on headless_job_leases;
create trigger trg_headless_job_leases_touch_updated
  before update on headless_job_leases
  for each row
  execute function headless_touch_updated_at();

drop trigger if exists trg_headless_webhook_events_touch_updated on headless_webhook_events;
create trigger trg_headless_webhook_events_touch_updated
  before update on headless_webhook_events
  for each row
  execute function headless_touch_updated_at();

-- Row Level Security setup (service-role only)
alter table headless_workers enable row level security;
alter table headless_job_leases enable row level security;
alter table headless_webhook_events enable row level security;

create policy if not exists headless_workers_service_access
  on headless_workers
  using (auth.role() = 'service_role')
  with check (auth.role() = 'service_role');

create policy if not exists headless_job_leases_service_access
  on headless_job_leases
  using (auth.role() = 'service_role')
  with check (auth.role() = 'service_role');

create policy if not exists headless_webhook_events_service_access
  on headless_webhook_events
  using (auth.role() = 'service_role')
  with check (auth.role() = 'service_role');

-- Helper views removed - columns referenced don't exist in simplified schema

reset search_path;
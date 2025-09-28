-- Phase 2: Public schema tables for headless chart service multi-worker coordination
-- Using public schema since PostgREST doesn't expose custom schemas

-- Ensure required extensions are available
create extension if not exists pgcrypto;

-- First create the headless_jobs table if it doesn't exist
create table if not exists public.headless_jobs (
  id uuid primary key default gen_random_uuid(),
  type text not null,
  symbol text not null,
  interval text not null,
  webhook_url text,
  status text not null check (status in ('pending', 'in_progress', 'completed', 'failed', 'cancelled')) default 'pending',
  result jsonb,
  error text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now()),
  started_at timestamptz,
  completed_at timestamptz
);

-- Worker instances table for tracking active workers
create table if not exists public.headless_workers (
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
  on public.headless_workers (status, last_heartbeat desc);

create index if not exists idx_headless_workers_hostname
  on public.headless_workers (hostname);

-- Job leases table for distributed job processing
create table if not exists public.headless_job_leases (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references public.headless_jobs(id) on delete cascade,
  worker_id text not null references public.headless_workers(id) on delete cascade,
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
  on public.headless_job_leases (job_id, worker_id);

create index if not exists idx_headless_job_leases_status_expires
  on public.headless_job_leases (status, lease_expires_at);

create index if not exists idx_headless_job_leases_token
  on public.headless_job_leases (lease_token);

-- Webhook events table for tracking delivery attempts
create table if not exists public.headless_webhook_events (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references public.headless_jobs(id) on delete cascade,
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
  on public.headless_webhook_events (job_id, event_type);

create index if not exists idx_headless_webhook_events_status_next_attempt
  on public.headless_webhook_events (status, next_attempt_at) 
  where status in ('pending', 'failed');

create index if not exists idx_headless_webhook_events_created_at
  on public.headless_webhook_events (created_at desc);

-- Function to update updated_at timestamp
create or replace function public.headless_touch_updated_at()
returns trigger as $$
begin
  new.updated_at = timezone('utc', now());
  return new;
end;
$$ language plpgsql;

-- Trigger to keep updated_at in sync for new tables
drop trigger if exists trg_headless_workers_touch_updated on public.headless_workers;
create trigger trg_headless_workers_touch_updated
  before update on public.headless_workers
  for each row
  execute function public.headless_touch_updated_at();

drop trigger if exists trg_headless_job_leases_touch_updated on public.headless_job_leases;
create trigger trg_headless_job_leases_touch_updated
  before update on public.headless_job_leases
  for each row
  execute function public.headless_touch_updated_at();

drop trigger if exists trg_headless_webhook_events_touch_updated on public.headless_webhook_events;
create trigger trg_headless_webhook_events_touch_updated
  before update on public.headless_webhook_events
  for each row
  execute function public.headless_touch_updated_at();

drop trigger if exists trg_headless_jobs_touch_updated on public.headless_jobs;
create trigger trg_headless_jobs_touch_updated
  before update on public.headless_jobs
  for each row
  execute function public.headless_touch_updated_at();

-- Row Level Security setup (disabled by default, enable if needed)
-- alter table public.headless_workers enable row level security;
-- alter table public.headless_job_leases enable row level security;
-- alter table public.headless_webhook_events enable row level security;
-- alter table public.headless_jobs enable row level security;

-- Grant necessary permissions (adjust as needed)
grant usage on schema public to postgres, anon, authenticated, service_role;
grant all on all tables in schema public to service_role;
grant all on all sequences in schema public to service_role;
grant all on all functions in schema public to service_role;
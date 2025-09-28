-- Phase 1: Supabase schema for headless chart service job persistence
-- Creates tables, indexes, triggers, and RLS policies supporting the
-- priority queue and job lifecycle requirements.

-- Ensure required extensions are available
create extension if not exists pgcrypto;

-- Use dedicated schema for headless service artifacts (optional)
create schema if not exists headless;
set search_path to headless, public;

-- Main job table storing lifecycle metadata
create table if not exists headless_jobs (
  id uuid primary key,
  symbol text not null,
  timeframe text not null,
  commands text[] default array[]::text[],
  vision_model text,
  metadata jsonb not null default '{}'::jsonb,
  status text not null check (status in (
    'pending', 'queued', 'in_progress', 'succeeded', 'failed'
  )),
  priority integer not null default 100,
  attempts integer not null default 0,
  queued_at timestamptz,
  started_at timestamptz,
  finished_at timestamptz,
  wait_time_ms integer,
  duration_ms integer,
  error text,
  snapshot jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create index if not exists idx_headless_jobs_status_priority
  on headless_jobs (status, priority, queued_at);

create index if not exists idx_headless_jobs_updated_at
  on headless_jobs (updated_at desc);

-- Queue table storing ordering metadata for pending jobs
create table if not exists headless_queue (
  job_id uuid primary key references headless_jobs(id) on delete cascade,
  priority integer not null,
  queued_at timestamptz not null default timezone('utc', now()),
  queue_position integer,
  last_heartbeat timestamptz,
  created_at timestamptz not null default timezone('utc', now())
);

create index if not exists idx_headless_queue_priority
  on headless_queue (priority, queued_at, job_id);

-- Historical audit of job status transitions
create table if not exists headless_job_history (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references headless_jobs(id) on delete cascade,
  from_status text,
  to_status text,
  note text,
  created_at timestamptz not null default timezone('utc', now())
);

create index if not exists idx_headless_job_history_job_id
  on headless_job_history (job_id, created_at desc);

-- Trigger to keep updated_at in sync
create or replace function headless_touch_updated_at()
returns trigger as $$
begin
  new.updated_at := timezone('utc', now());
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_headless_jobs_touch_updated on headless_jobs;
create trigger trg_headless_jobs_touch_updated
  before update on headless_jobs
  for each row
  execute function headless_touch_updated_at();

-- Row Level Security setup (service-role only)
alter table headless_jobs enable row level security;
alter table headless_queue enable row level security;
alter table headless_job_history enable row level security;

create policy if not exists headless_jobs_service_access
  on headless_jobs
  using (auth.role() = 'service_role')
  with check (auth.role() = 'service_role');

create policy if not exists headless_queue_service_access
  on headless_queue
  using (auth.role() = 'service_role')
  with check (auth.role() = 'service_role');

create policy if not exists headless_job_history_service_access
  on headless_job_history
  using (auth.role() = 'service_role')
  with check (auth.role() = 'service_role');

-- Optional helper view for metrics aggregation
create view if not exists headless_job_metrics as
select
  count(*) filter (where status in ('pending', 'queued')) as pending_jobs,
  count(*) filter (where status = 'in_progress') as in_progress_jobs,
  count(*) filter (where status = 'succeeded') as succeeded_jobs,
  count(*) filter (where status = 'failed') as failed_jobs,
  coalesce(avg(wait_time_ms), 0)::bigint as avg_wait_ms,
  coalesce(avg(duration_ms), 0)::bigint as avg_duration_ms,
  timezone('utc', now()) as captured_at
from headless_jobs;

reset search_path;

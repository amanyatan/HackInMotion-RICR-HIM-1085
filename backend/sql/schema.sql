-- ============================================================================
-- COSMOS backend schema (Supabase / Postgres)
--
-- Apply this in the Supabase SQL editor. Row-Level Security keeps every row
-- scoped to the owning `auth.uid()`.
--
-- Core tables: profiles, onboarding, user_preferences, conversations,
-- notes, study_sessions, study_events, dashboard_stats, abuse_events.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- profiles — display metadata for a signed-in user (optional but recommended)
-- ---------------------------------------------------------------------------
create table if not exists public.profiles (
  id          uuid primary key references auth.users (id) on delete cascade,
  email       text,
  name        text,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);

alter table public.profiles enable row level security;

create policy "profiles_select_own" on public.profiles
  for select using (auth.uid() = id);
create policy "profiles_insert_own" on public.profiles
  for insert with check (auth.uid() = id);
create policy "profiles_update_own" on public.profiles
  for update using (auth.uid() = id);

-- ---------------------------------------------------------------------------
-- onboarding — one row per user tracking the setup wizard + saved answers
-- ---------------------------------------------------------------------------
create table if not exists public.onboarding (
  uid             uuid primary key references auth.users (id) on delete cascade,
  current_step    int  default 1,
  done            boolean default false,
  name            text,
  reason          text,
  subjects        text[],          -- e.g. {"mathematics","physics"}
  language        text default 'en',
  character       text default 'kei',
  character_voice text,
  updated_at      timestamptz default now()
);

alter table public.onboarding enable row level security;

create policy "onboarding_select_own" on public.onboarding
  for select using (auth.uid() = uid);
create policy "onboarding_insert_own" on public.onboarding
  for insert with check (auth.uid() = uid);
create policy "onboarding_update_own" on public.onboarding
  for update using (auth.uid() = uid);

-- ---------------------------------------------------------------------------
-- user_preferences — selected companion character / language
-- ---------------------------------------------------------------------------
create table if not exists public.user_preferences (
  uid        uuid primary key references auth.users (id) on delete cascade,
  character  text default 'kei',
  language   text default 'en',
  updated_at timestamptz default now()
);

alter table public.user_preferences enable row level security;

create policy "prefs_select_own" on public.user_preferences
  for select using (auth.uid() = uid);
create policy "prefs_insert_own" on public.user_preferences
  for insert with check (auth.uid() = uid);
create policy "prefs_update_own" on public.user_preferences
  for update using (auth.uid() = uid);

-- ---------------------------------------------------------------------------
-- conversations — companion chat messages (role: user | assistant)
-- ---------------------------------------------------------------------------
create table if not exists public.conversations (
  id         uuid primary key default gen_random_uuid(),
  uid        uuid references auth.users (id) on delete cascade not null,
  role       text not null check (role in ('user', 'assistant')),
  content    text not null,
  character  text default 'kei',
  language   text default 'en',
  emotion    text,
  created_at timestamptz default now()
);

create index if not exists idx_conversations_uid on public.conversations (uid, created_at desc);

alter table public.conversations enable row level security;

create policy "conversations_select_own" on public.conversations
  for select using (auth.uid() = uid);
create policy "conversations_insert_own" on public.conversations
  for insert with check (auth.uid() = uid);
create policy "conversations_delete_own" on public.conversations
  for delete using (auth.uid() = uid);

-- ---------------------------------------------------------------------------
-- notes — user study notes / saved passages
-- ---------------------------------------------------------------------------
create table if not exists public.notes (
  id         uuid primary key default gen_random_uuid(),
  uid        uuid references auth.users (id) on delete cascade not null,
  subject    text not null,
  title      text not null,
  content    text not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists idx_notes_uid on public.notes (uid, updated_at desc);

alter table public.notes enable row level security;

create policy "notes_select_own" on public.notes
  for select using (auth.uid() = uid);
create policy "notes_insert_own" on public.notes
  for insert with check (auth.uid() = uid);
create policy "notes_update_own" on public.notes
  for update using (auth.uid() = uid);
create policy "notes_delete_own" on public.notes
  for delete using (auth.uid() = uid);

-- ---------------------------------------------------------------------------
-- study_sessions — one row per study session lifecycle
-- ---------------------------------------------------------------------------
create table if not exists public.study_sessions (
  id               uuid primary key default gen_random_uuid(),
  uid              uuid references auth.users (id) on delete cascade not null,
  character        text default 'kei',
  language         text default 'en',
  subject          text,
  status           text default 'in_progress'
                   check (status in ('in_progress', 'paused', 'completed')),
  duration_seconds int default 0,
  started_at       timestamptz default now(),
  ended_at         timestamptz
);

create index if not exists idx_study_sessions_uid on public.study_sessions (uid, started_at desc);

alter table public.study_sessions enable row level security;

create policy "sessions_select_own" on public.study_sessions
  for select using (auth.uid() = uid);
create policy "sessions_insert_own" on public.study_sessions
  for insert with check (auth.uid() = uid);
create policy "sessions_update_own" on public.study_sessions
  for update using (auth.uid() = uid);

-- ---------------------------------------------------------------------------
-- study_events — granular events within a session (word typed, read time, etc.)
-- ---------------------------------------------------------------------------
create table if not exists public.study_events (
  id         uuid primary key default gen_random_uuid(),
  session_id uuid references public.study_sessions (id) on delete cascade,
  uid        uuid references auth.users (id) on delete cascade not null,
  type       text not null,
  payload    jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

create index if not exists idx_study_events_session on public.study_events (session_id);

alter table public.study_events enable row level security;

create policy "events_select_own" on public.study_events
  for select using (auth.uid() = uid);
create policy "events_insert_own" on public.study_events
  for insert with check (auth.uid() = uid);

-- ---------------------------------------------------------------------------
-- study_plans — saved session schedules (hours + breaks) generated with the
-- companion during Study Mode setup
-- ---------------------------------------------------------------------------
create table if not exists public.study_plans (
  id           uuid primary key default gen_random_uuid(),
  uid          uuid references auth.users (id) on delete cascade not null,
  total_hours  numeric not null,
  breaks_count int default 0,
  plan         jsonb default '{}'::jsonb,
  created_at   timestamptz default now()
);

create index if not exists idx_study_plans_uid on public.study_plans (uid, created_at desc);

alter table public.study_plans enable row level security;

create policy "plans_select_own" on public.study_plans
  for select using (auth.uid() = uid);
create policy "plans_insert_own" on public.study_plans
  for insert with check (auth.uid() = uid);
create policy "plans_delete_own" on public.study_plans
  for delete using (auth.uid() = uid);

-- ---------------------------------------------------------------------------
-- dashboard_stats — daily aggregates (words_typed, minutes_studied)
-- ---------------------------------------------------------------------------
create table if not exists public.dashboard_stats (
  id              uuid primary key default gen_random_uuid(),
  uid             uuid references auth.users (id) on delete cascade not null,
  date            date not null,
  words_typed     int default 0,
  minutes_studied int default 0,
  updated_at      timestamptz default now(),
  unique (uid, date)
);

alter table public.dashboard_stats enable row level security;

create policy "stats_select_own" on public.dashboard_stats
  for select using (auth.uid() = uid);
create policy "stats_insert_own" on public.dashboard_stats
  for insert with check (auth.uid() = uid);
create policy "stats_update_own" on public.dashboard_stats
  for update using (auth.uid() = uid);

-- ---------------------------------------------------------------------------
-- abuse_events — audit log of flagged/moderated inputs (best-effort)
-- ---------------------------------------------------------------------------
create table if not exists public.abuse_events (
  id         uuid primary key default gen_random_uuid(),
  uid        uuid references auth.users (id) on delete cascade,
  reason     text,
  terms      text[],
  input      text,
  created_at timestamptz default now()
);

alter table public.abuse_events enable row level security;

create policy "abuse_insert_own" on public.abuse_events
  for insert with check (auth.uid() = uid);

-- ============================================================================
-- Convenience: create an app-level role usable for backend service access.
-- The backend uses the SUPABASE_SERVICE_ROLE_KEY (bypasses RLS) already, so
-- this is optional. Storing per-user RLS ids is the recommended path.
-- ============================================================================

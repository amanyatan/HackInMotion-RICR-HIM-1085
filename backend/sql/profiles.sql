-- Optional: COSMOS `profiles` table, linked to Supabase Auth user IDs.
--
-- Run this in the Supabase SQL editor (Project -> SQL -> New query).
-- Auth works without it; this only stores the display name from signup.
--
-- Password storage is handled entirely by Supabase Auth (hashed/bcrypt).
-- NEVER store plaintext passwords in your own tables.

create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  email text not null,
  name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.profiles enable row level security;

create policy "Profiles are viewable by the owner"
  on public.profiles for select
  using (auth.uid() = id);

create policy "Profiles are insertable by the owner"
  on public.profiles for insert
  with check (auth.uid() = id);

create policy "Profiles are updateable by the owner"
  on public.profiles for update
  using (auth.uid() = id);

-- Service-role operations (backend) bypass RLS automatically.
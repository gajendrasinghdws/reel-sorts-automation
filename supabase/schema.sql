create extension if not exists pgcrypto;

create table if not exists public.instagram_accounts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  username text not null,
  normalized_username text not null,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  unique(user_id, normalized_username)
);

create table if not exists public.reels (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  instagram_account_id uuid references public.instagram_accounts(id) on delete set null,
  instagram_url text,
  source_media_id text,
  source_key text not null,
  caption text,
  title_hint text,
  local_sha256 text,
  drive_file_id text,
  drive_file_name text,
  downloaded_at timestamptz,
  uploaded_at timestamptz,
  drive_deleted_at timestamptz,
  youtube_video_id text,
  status text not null default 'queued'
    check (status in ('queued','downloading','downloaded','uploading','uploaded','failed','skipped')),
  error_message text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(user_id, source_key)
);

create index if not exists reels_status_idx on public.reels(status);
create index if not exists reels_created_idx on public.reels(created_at);
create index if not exists reels_downloaded_idx on public.reels(downloaded_at);
create index if not exists reels_uploaded_idx on public.reels(uploaded_at);

create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists reels_touch_updated_at on public.reels;
create trigger reels_touch_updated_at
before update on public.reels
for each row execute function public.touch_updated_at();

alter table public.instagram_accounts enable row level security;
alter table public.reels enable row level security;

revoke all on table public.instagram_accounts from anon;
revoke all on table public.reels from anon;

grant select, insert, update, delete on table public.instagram_accounts to authenticated;
grant select, insert, update, delete on table public.reels to authenticated;

drop policy if exists "accounts_select_own" on public.instagram_accounts;
create policy "accounts_select_own"
on public.instagram_accounts for select to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "accounts_insert_own" on public.instagram_accounts;
create policy "accounts_insert_own"
on public.instagram_accounts for insert to authenticated
with check ((select auth.uid()) = user_id);

drop policy if exists "accounts_update_own" on public.instagram_accounts;
create policy "accounts_update_own"
on public.instagram_accounts for update to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

drop policy if exists "accounts_delete_own" on public.instagram_accounts;
create policy "accounts_delete_own"
on public.instagram_accounts for delete to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "reels_select_own" on public.reels;
create policy "reels_select_own"
on public.reels for select to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "reels_insert_own" on public.reels;
create policy "reels_insert_own"
on public.reels for insert to authenticated
with check ((select auth.uid()) = user_id);

drop policy if exists "reels_update_own" on public.reels;
create policy "reels_update_own"
on public.reels for update to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

drop policy if exists "reels_delete_own" on public.reels;
create policy "reels_delete_own"
on public.reels for delete to authenticated
using ((select auth.uid()) = user_id);

-- Backend jobs use SUPABASE_SERVICE_ROLE_KEY and therefore bypass RLS.

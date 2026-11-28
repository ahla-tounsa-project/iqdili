-- Deduplicate page-view events by a random, per-tab session token.
-- The token is generated client-side with crypto.randomUUID() and stored
-- only in sessionStorage for at most 30 minutes. No IP address, account ID,
-- device ID, or fingerprint is stored.
create table if not exists private.site_page_view_sessions (
  session_id uuid not null,
  page_key text not null check (page_key in
    ('home','services','jobs','realty','market','good','guide','cv','ask','saved','account')),
  last_counted_at timestamptz not null default now(),
  primary key (session_id, page_key)
);

create index if not exists site_page_view_sessions_last_counted_idx
  on private.site_page_view_sessions (last_counted_at);

alter table private.site_page_view_sessions enable row level security;
revoke all privileges on table private.site_page_view_sessions from public, anon, authenticated;

create or replace function public.record_site_page_view(p_page_key text, p_session_id uuid)
returns void
language plpgsql
security definer
set search_path to ''
as $function$
declare
  v_day date := (now() at time zone 'Africa/Tunis')::date;
  v_rows integer;
begin
  if p_session_id is null then
    raise exception 'session token required' using errcode = '22023';
  end if;

  if p_page_key is null or p_page_key not in
    ('home','services','jobs','realty','market','good','guide','cv','ask','saved','account') then
    raise exception 'invalid page key' using errcode = '22023';
  end if;

  if auth.uid() is not null then
    if public.is_admin() or public.is_owner() then
      return;
    end if;
  end if;

  -- Count the same page at most once per random tab token in each 30-minute window.
  insert into private.site_page_view_sessions (session_id, page_key, last_counted_at)
  values (p_session_id, p_page_key, now())
  on conflict (session_id, page_key)
  do update set last_counted_at = excluded.last_counted_at
    where private.site_page_view_sessions.last_counted_at < now() - interval '30 minutes';

  get diagnostics v_rows = row_count;

  if v_rows > 0 then
    insert into private.site_page_daily_counts (visit_day, page_key, view_count)
    values (v_day, p_page_key, 1), (v_day, '__all__', 1)
    on conflict (visit_day, page_key)
    do update set view_count = private.site_page_daily_counts.view_count + 1;
  end if;
end;
$function$;

-- The old one-argument endpoint cannot deduplicate sessions, so disable it.
revoke all on function public.record_site_page_view(text) from public, anon, authenticated;
revoke all on function public.record_site_page_view(text, uuid) from public;
grant execute on function public.record_site_page_view(text, uuid) to anon, authenticated;

do $migration$
begin
  if not exists (select 1 from cron.job where jobname = 'cleanup-site-page-view-sessions') then
    perform cron.schedule(
      'cleanup-site-page-view-sessions',
      '* * * * *',
      'delete from private.site_page_view_sessions where last_counted_at < now() - interval ''30 minutes'';'
    );
  end if;
end
$migration$;

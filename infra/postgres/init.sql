create schema if not exists raw;
create schema if not exists analytics;
create schema if not exists governance;
create table if not exists governance.metric_audit (
  audit_id bigserial primary key,
  metric_name text not null,
  metric_version integer not null,
  registry_sha256 text not null,
  evaluated_at timestamptz not null default now(),
  result numeric,
  status text not null check (status in ('pass','warn','fail'))
);

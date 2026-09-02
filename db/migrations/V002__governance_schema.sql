create table if not exists governance.pipeline_run (
  run_id uuid primary key,
  git_sha text not null,
  dataset_version text not null,
  started_at timestamptz not null,
  completed_at timestamptz,
  status text not null check (status in ('running','passed','failed')),
  records_processed bigint not null default 0
);

create table if not exists governance.metric_definition (
  metric_name text not null,
  version integer not null,
  label text not null,
  owner_team text not null,
  grain text not null,
  business_definition text not null,
  sql_expression text not null,
  effective_from date not null,
  primary key (metric_name, version)
);

create table if not exists governance.metric_evaluation (
  evaluation_id bigserial primary key,
  run_id uuid not null references governance.pipeline_run(run_id),
  metric_name text not null,
  definition_version integer not null,
  team_name text not null,
  governed_value numeric(24,4) not null,
  reported_value numeric(24,4) not null,
  absolute_delta numeric(24,4) not null,
  relative_delta numeric(18,8),
  status text not null check (status in ('certified','drifted')),
  evaluated_at timestamptz not null default now()
);

create schema if not exists raw;
create schema if not exists analytics;
create schema if not exists governance;

create table if not exists raw.orders (
  order_id text primary key,
  opened_date date not null,
  closed_date date,
  status text not null check (status in ('open','closed','cancelled')),
  region text not null,
  product text not null,
  channel text not null,
  order_value numeric(18,2) not null check (order_value >= 0),
  source_updated_at date not null
);

create table if not exists raw.escrow_events (
  event_id text primary key,
  order_id text not null references raw.orders(order_id),
  event_type text not null,
  event_date date not null,
  sequence integer not null check (sequence > 0)
);

create table if not exists raw.finance_transactions (
  transaction_id text primary key,
  order_id text not null references raw.orders(order_id),
  transaction_date date not null,
  transaction_type text not null check (transaction_type in ('recognized_revenue','refund')),
  amount numeric(18,2) not null,
  currency char(3) not null
);

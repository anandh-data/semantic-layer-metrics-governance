create index if not exists ix_orders_closed_region on raw.orders(closed_date, region) where status = 'closed';
create index if not exists ix_escrow_order_date on raw.escrow_events(order_id, event_date);
create index if not exists ix_finance_order_date on raw.finance_transactions(order_id, transaction_date);
create index if not exists ix_metric_eval_run_status on governance.metric_evaluation(run_id, status);

with governed as (
  select sum(net_revenue) as value from analytics.metric_daily_performance
), finance_team as (
  select sum(amount) as value from raw.finance_transactions
), operations_team as (
  select sum(order_value * 0.0065) as value from raw.orders where status = 'closed'
), commercial_team as (
  select sum(order_value * 0.0065) as value from raw.orders where status <> 'cancelled'
)
select 'net_revenue' as metric_name, 'finance' as team_name, governed.value as governed_value, finance_team.value as reported_value from governed, finance_team
union all
select 'net_revenue', 'operations', governed.value, operations_team.value from governed, operations_team
union all
select 'net_revenue', 'commercial', governed.value, commercial_team.value from governed, commercial_team;

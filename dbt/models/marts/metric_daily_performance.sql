select
  coalesce(closed_date, opened_date) as metric_date,
  region,
  count(*) filter (where status = 'closed') as closed_orders,
  sum(gross_revenue) as gross_revenue,
  sum(refunds) as refunds,
  sum(net_revenue) as net_revenue,
  avg(turnaround_days) filter (where status = 'closed') as average_turnaround_days
from {{ ref('fct_order_performance') }}
group by 1,2

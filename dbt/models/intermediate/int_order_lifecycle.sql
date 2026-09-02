select
  o.order_id,
  o.region,
  o.product,
  o.channel,
  o.status,
  o.opened_date,
  o.closed_date,
  o.order_value,
  case when o.closed_date is not null then o.closed_date - o.opened_date end as turnaround_days,
  coalesce(sum(case when f.transaction_type = 'recognized_revenue' then f.amount else 0 end), 0) as gross_revenue,
  coalesce(sum(case when f.transaction_type = 'refund' then f.amount else 0 end), 0) as refunds,
  coalesce(sum(f.amount), 0) as net_revenue
from {{ ref('stg_orders') }} o
left join {{ ref('stg_finance_transactions') }} f using (order_id)
group by 1,2,3,4,5,6,7,8

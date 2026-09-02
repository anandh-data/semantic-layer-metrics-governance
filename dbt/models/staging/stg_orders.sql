select
  order_id,
  cast(opened_date as date) as opened_date,
  nullif(closed_date, '')::date as closed_date,
  lower(status) as status,
  upper(region) as region,
  cast(order_amount as numeric(18,2)) as order_amount
from {{ ref('orders') }}

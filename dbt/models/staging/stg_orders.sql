select
  order_id,
  cast(opened_date as date) as opened_date,
  cast(closed_date as date) as closed_date,
  lower(status) as status,
  upper(region) as region,
  product,
  channel,
  cast(order_value as numeric(18,2)) as order_value,
  source_updated_at
from {{ source('raw', 'orders') }}

select
  transaction_id,
  order_id,
  cast(transaction_date as date) as transaction_date,
  lower(transaction_type) as transaction_type,
  cast(amount as numeric(18,2)) as amount
from {{ ref('finance_transactions') }}

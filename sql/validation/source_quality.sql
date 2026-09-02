select 'orphan_escrow_event' as check_name, count(*) as failures
from raw.escrow_events e left join raw.orders o using (order_id) where o.order_id is null
union all
select 'orphan_finance_transaction', count(*)
from raw.finance_transactions f left join raw.orders o using (order_id) where o.order_id is null
union all
select 'closed_without_close_date', count(*) from raw.orders where status = 'closed' and closed_date is null
union all
select 'close_before_open', count(*) from raw.orders where closed_date < opened_date
union all
select 'non_usd_transaction', count(*) from raw.finance_transactions where currency <> 'USD';

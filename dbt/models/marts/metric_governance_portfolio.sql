with hmda as (
  select * from {{ ref('stg_hmda_applications') }}
), orders as (
  select * from {{ ref('fct_order_performance') }}
), h as (
  select
    count(*)::numeric as hmda_records,
    count(*) filter (where action_taken in (1,2,3))::numeric as applications_decided,
    count(*) filter (where action_taken = 1)::numeric as originated_loans,
    count(*) filter (where action_taken = 2)::numeric as approved_not_accepted,
    count(*) filter (where action_taken = 3)::numeric as denied_applications,
    count(*) filter (where action_taken = 4)::numeric as withdrawn_applications,
    count(*) filter (where action_taken = 5)::numeric as incomplete_applications,
    avg(loan_amount_000s) filter (where loan_amount_000s > 0)::numeric as average_loan_amount_000s,
    percentile_cont(0.5) within group (order by loan_amount_000s) filter (where loan_amount_000s > 0)::numeric as median_loan_amount_000s,
    avg(applicant_income_000s) filter (where applicant_income_000s > 0)::numeric as average_applicant_income_000s,
    count(*) filter (where loan_type = 1)::numeric / count(*) as conventional_share,
    count(*) filter (where loan_type = 2)::numeric / count(*) as fha_share,
    count(*) filter (where loan_type = 3)::numeric / count(*) as va_share,
    count(*) filter (where loan_purpose = 1)::numeric / count(*) as home_purchase_share,
    count(*) filter (where loan_purpose = 3)::numeric / count(*) as refinance_share
  from hmda
), o as (
  select
    count(*)::numeric as order_count,
    count(*) filter (where status = 'closed')::numeric as closed_orders,
    count(*) filter (where status = 'open')::numeric as open_orders,
    count(*) filter (where status = 'cancelled')::numeric / count(*) as cancellation_rate,
    count(*) filter (where status = 'closed')::numeric / count(*) as close_rate,
    avg(order_value)::numeric as average_order_value,
    sum(order_value) filter (where status = 'closed')::numeric as closed_order_value,
    sum(net_revenue)::numeric as net_revenue,
    avg(turnaround_days) filter (where status = 'closed')::numeric as average_turnaround_days
  from orders
), metrics as (
  select 'hmda_records' metric_name, hmda_records metric_value from h union all
  select 'applications_decided', applications_decided from h union all
  select 'originated_loans', originated_loans from h union all
  select 'approved_not_accepted', approved_not_accepted from h union all
  select 'denied_applications', denied_applications from h union all
  select 'withdrawn_applications', withdrawn_applications from h union all
  select 'incomplete_applications', incomplete_applications from h union all
  select 'denial_rate', denied_applications / nullif(applications_decided,0) from h union all
  select 'origination_rate', originated_loans / nullif(applications_decided,0) from h union all
  select 'average_loan_amount_000s', average_loan_amount_000s from h union all
  select 'median_loan_amount_000s', median_loan_amount_000s from h union all
  select 'average_applicant_income_000s', average_applicant_income_000s from h union all
  select 'conventional_share', conventional_share from h union all
  select 'fha_share', fha_share from h union all
  select 'va_share', va_share from h union all
  select 'home_purchase_share', home_purchase_share from h union all
  select 'refinance_share', refinance_share from h union all
  select 'order_count', order_count from o union all
  select 'closed_orders', closed_orders from o union all
  select 'open_orders', open_orders from o union all
  select 'cancellation_rate', cancellation_rate from o union all
  select 'close_rate', close_rate from o union all
  select 'average_order_value', average_order_value from o union all
  select 'closed_order_value', closed_order_value from o union all
  select 'net_revenue', net_revenue from o
)
select metric_name, metric_value from metrics

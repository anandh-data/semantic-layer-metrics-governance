select * from {{ ref('fct_order_performance') }} where turnaround_days < 0

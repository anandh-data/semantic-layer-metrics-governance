select event_id, order_id, lower(event_type) as event_type, cast(event_date as date) as event_date, sequence
from {{ source('raw', 'escrow_events') }}

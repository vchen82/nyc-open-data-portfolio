select complaint_id, event_date as date_key, event_date, event_hour,
  location_key, problem_key, region_key, status, 1 as complaint_count
from {{ ref('stg_nyc_311_vehicle_complaints') }}

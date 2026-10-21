select crash_id, event_date as date_key, event_date, event_hour,
  location_key, 1 as crash_count,
persons_injured, persons_killed, pedestrians_injured, pedestrians_killed, cyclist_injured, cyclist_killed, motorist_injured, motorist_killed
from {{ ref('stg_nyc_vehicle_crashes') }}

with ranked as (
  select *, row_number() over (partition by collision_id order by _ingested_at desc) as row_rank
  from {{ source('nyc_raw', 'source_nyc_vehicle_crashes') }}
), cleaned as (
  select nullif(trim(collision_id), '') as crash_id,
    cast({{ safe_cast('crash_date', 'datetime' if target.type == 'bigquery' else 'timestamp') }} as date) as event_date,
    {{ safe_cast('crash_time', 'time') }} as crash_time,
    nullif({{ norm('borough') }}, 'UNSPECIFIED') as borough,
    {{ zip_code('zip_code') }} as zip_code,
    {{ norm('on_street_name') }} as street_name,
    {{ safe_cast("number_of_persons_injured", "integer") }} as persons_injured,
    {{ safe_cast("number_of_persons_killed", "integer") }} as persons_killed,
    {{ safe_cast("number_of_pedestrians_injured", "integer") }} as pedestrians_injured,
    {{ safe_cast("number_of_pedestrians_killed", "integer") }} as pedestrians_killed,
    {{ safe_cast("number_of_cyclist_injured", "integer") }} as cyclist_injured,
    {{ safe_cast("number_of_cyclist_killed", "integer") }} as cyclist_killed,
    {{ safe_cast("number_of_motorist_injured", "integer") }} as motorist_injured,
    {{ safe_cast("number_of_motorist_killed", "integer") }} as motorist_killed,
    {{ norm("contributing_factor_vehicle_1") }} as contributing_factor_vehicle_1,
    {{ norm("contributing_factor_vehicle_2") }} as contributing_factor_vehicle_2,
    {{ norm("contributing_factor_vehicle_3") }} as contributing_factor_vehicle_3,
    {{ norm("contributing_factor_vehicle_4") }} as contributing_factor_vehicle_4,
    {{ norm("contributing_factor_vehicle_5") }} as contributing_factor_vehicle_5,
    {{ norm("vehicle_type_code1") }} as vehicle_type_code1,
    {{ norm("vehicle_type_code2") }} as vehicle_type_code2,
    {{ norm("vehicle_type_code_3") }} as vehicle_type_code_3,
    {{ norm("vehicle_type_code_4") }} as vehicle_type_code_4,
    {{ norm("vehicle_type_code_5") }} as vehicle_type_code_5
  from ranked where row_rank = 1
)
select *, {{ date_part('hour','crash_time') }} as event_hour,
  {{ key(['borough', 'zip_code', 'street_name']) }} as location_key
from cleaned

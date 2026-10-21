-- One dimension member per normalized borough/ZIP/street tuple, including unknowns.
select distinct location_key, borough, zip_code, street_name
from (
  select location_key, borough, zip_code, street_name from {{ ref('stg_nyc_311_vehicle_complaints') }}
  union all
  select location_key, borough, zip_code, street_name from {{ ref('stg_nyc_vehicle_crashes') }}
) locations

-- Observed dates. Reporting views retain observed rows; missing dates are not imputed.
with dates as (
  select event_date from {{ ref('stg_nyc_311_vehicle_complaints') }}
  union
  select event_date from {{ ref('stg_nyc_vehicle_crashes') }}
)
select event_date as date_key, event_date,
  {{ date_part('year','event_date') }} as year,
  {{ date_part('month','event_date') }} as month,
  {{ date_part('day','event_date') }} as day,
  case when extract(month from event_date) in (12, 1, 2) then 'Winter'
       when extract(month from event_date) in (3, 4, 5) then 'Spring'
       when extract(month from event_date) in (6, 7, 8) then 'Summer'
       else 'Fall' end as season
from dates where event_date is not null

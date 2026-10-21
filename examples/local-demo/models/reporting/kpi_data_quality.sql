select 'complaints' as source, count(*) as total_records,
  sum(case when complaint_id is null then 1 else 0 end) as missing_id,
  sum(case when event_date is null then 1 else 0 end) as missing_date,
  sum(case when zip_code is null then 1 else 0 end) as missing_zip,
  sum(case when street_name is null then 1 else 0 end) as missing_street
from {{ ref('stg_nyc_311_vehicle_complaints') }}
union all
select 'crashes', count(*),
  sum(case when crash_id is null then 1 else 0 end),
  sum(case when event_date is null then 1 else 0 end),
  sum(case when zip_code is null then 1 else 0 end),
  sum(case when street_name is null then 1 else 0 end)
from {{ ref('stg_nyc_vehicle_crashes') }}

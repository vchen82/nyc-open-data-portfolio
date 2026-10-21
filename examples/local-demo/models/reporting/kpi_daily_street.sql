with complaints as (
  select f.event_date, l.borough, l.zip_code, l.street_name, count(*) as complaints,
    sum(case when p.complaint_type = 'ILLEGAL PARKING' then 1 else 0 end) as parking_complaints
  from {{ ref('fact_311_vehicle_complaints') }} f
  join {{ ref('dim_shared_location') }} l on f.location_key = l.location_key
  join {{ ref('dim_problem_details') }} p on f.problem_key = p.problem_key
  where f.event_date >= cast('{{ var("analysis_start") }}' as date)
    and f.event_date < cast('{{ var("analysis_end") }}' as date)
    and l.zip_code is not null
    and l.street_name is not null

  group by f.event_date, l.borough, l.zip_code, l.street_name
), crashes as (
  select f.event_date, l.borough, l.zip_code, l.street_name, count(*) as crashes,
    sum(coalesce(f.persons_injured, 0)) as persons_injured,
    sum(coalesce(f.persons_killed, 0)) as persons_killed,
    sum(coalesce(f.pedestrians_injured, 0) + coalesce(f.cyclist_injured, 0)) as vulnerable_injuries,
    sum(case when f.persons_injured is null or f.persons_killed is null
      or f.pedestrians_injured is null or f.cyclist_injured is null then 1 else 0 end) as crashes_with_missing_measures
  from {{ ref('fact_vehicle_crashes') }} f
  join {{ ref('dim_shared_location') }} l on f.location_key = l.location_key
  where f.event_date >= cast('{{ var("analysis_start") }}' as date)
    and f.event_date < cast('{{ var("analysis_end") }}' as date)
    and l.zip_code is not null
    and l.street_name is not null

  group by f.event_date, l.borough, l.zip_code, l.street_name
)
select coalesce(c.event_date, v.event_date) as event_date, coalesce(c.borough, v.borough) as borough, coalesce(c.zip_code, v.zip_code) as zip_code, coalesce(c.street_name, v.street_name) as street_name,
  coalesce(c.complaints, 0) as complaints, coalesce(c.parking_complaints, 0) as parking_complaints,
  coalesce(v.crashes, 0) as crashes, coalesce(v.persons_injured, 0) as persons_injured,
  coalesce(v.persons_killed, 0) as persons_killed, coalesce(v.vulnerable_injuries, 0) as vulnerable_injuries,
  coalesce(v.crashes_with_missing_measures, 0) as crashes_with_missing_measures
from complaints c full outer join crashes v
on c.event_date = v.event_date and (c.borough = v.borough or (c.borough is null and v.borough is null)) and (c.zip_code = v.zip_code or (c.zip_code is null and v.zip_code is null)) and (c.street_name = v.street_name or (c.street_name is null and v.street_name is null))

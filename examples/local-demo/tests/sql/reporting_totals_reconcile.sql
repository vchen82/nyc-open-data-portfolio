-- Checks aggregate-before-join behavior for known-ZIP records in the window.
with expected as (
  select
    (select count(*) from {{ ref('stg_nyc_311_vehicle_complaints') }}
      where zip_code is not null and event_date >= cast('{{ var("analysis_start") }}' as date)
        and event_date < cast('{{ var("analysis_end") }}' as date)) as complaints,
    (select count(*) from {{ ref('stg_nyc_vehicle_crashes') }}
      where zip_code is not null and event_date >= cast('{{ var("analysis_start") }}' as date)
        and event_date < cast('{{ var("analysis_end") }}' as date)) as crashes
), actual as (
  select coalesce(sum(complaints),0) as complaints, coalesce(sum(crashes),0) as crashes
  from {{ ref('kpi_daily_zip') }}
)
select e.* from expected e cross join actual a
where e.complaints <> a.complaints or e.crashes <> a.crashes

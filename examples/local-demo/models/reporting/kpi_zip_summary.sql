with totals as (
  select zip_code, sum(complaints) as complaints, sum(parking_complaints) as parking_complaints,
    sum(crashes) as crashes, sum(persons_injured) as persons_injured,
    sum(persons_killed) as persons_killed, sum(vulnerable_injuries) as vulnerable_injuries,
    sum(crashes_with_missing_measures) as crashes_with_missing_measures
  from {{ ref('kpi_daily_zip') }} group by zip_code
)
select *, {{ ratio('complaints','crashes') }} as complaints_per_crash,
  {{ ratio('persons_injured','crashes') }} as injuries_per_crash,
  case when parking_complaints >= {{ var('minimum_parking_complaints') }}
    and crashes_with_missing_measures = 0
    then {{ ratio('vulnerable_injuries','parking_complaints') }} end as vulnerable_injuries_per_parking_complaint,
  parking_complaints >= {{ var('minimum_parking_complaints') }} and crashes_with_missing_measures = 0 as injury_ratio_eligible
from totals

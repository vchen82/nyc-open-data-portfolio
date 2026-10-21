-- Complaint types have their own counts. Do not duplicate crash totals across these categories.
select p.complaint_type, count(*) as complaints
from {{ ref('fact_311_vehicle_complaints') }} f
join {{ ref('dim_problem_details') }} p on f.problem_key = p.problem_key
where f.event_date >= cast('{{ var("analysis_start") }}' as date)
  and f.event_date < cast('{{ var("analysis_end") }}' as date)
group by p.complaint_type order by complaints desc

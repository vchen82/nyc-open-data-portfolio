select {{ date_part('year', 'event_date') }} as year,
  {{ date_part('month', 'event_date') }} as month,
  sum(complaints) as complaints, sum(crashes) as crashes
from {{ ref('kpi_daily_zip') }}
group by {{ date_part('year', 'event_date') }}, {{ date_part('month', 'event_date') }}

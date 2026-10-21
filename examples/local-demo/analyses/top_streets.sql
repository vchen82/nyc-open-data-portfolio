select borough, zip_code, street_name, sum(crashes) as crashes,
  sum(parking_complaints) as illegal_parking_complaints
from {{ ref('kpi_daily_street') }}
group by borough, zip_code, street_name
order by crashes desc, borough, zip_code, street_name
limit 20

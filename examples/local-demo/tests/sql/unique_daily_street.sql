select event_date, borough, zip_code, street_name from {{ ref('kpi_daily_street') }}
group by event_date, borough, zip_code, street_name having count(*) > 1

select event_date, zip_code from {{ ref('kpi_daily_zip') }}
group by event_date, zip_code having count(*) > 1

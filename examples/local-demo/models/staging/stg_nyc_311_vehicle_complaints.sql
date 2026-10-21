with ranked as (
  select *, row_number() over (partition by unique_key order by _ingested_at desc) as row_rank
  from {{ source('nyc_raw', 'source_nyc_311_vehicle_complaints') }}
), cleaned as (
  select
    nullif(trim(unique_key), '') as complaint_id,
    {{ safe_cast('created_date', 'datetime' if target.type == 'bigquery' else 'timestamp') }} as created_at,
    {{ safe_cast('closed_date', 'datetime' if target.type == 'bigquery' else 'timestamp') }} as closed_at,
    {{ norm('agency') }} as agency,
    {{ norm('complaint_type') }} as complaint_type,
    {{ norm('descriptor') }} as descriptor,
    {{ norm('status') }} as status,
    nullif({{ norm('borough') }}, 'UNSPECIFIED') as borough,
    {{ zip_code('incident_zip') }} as zip_code,
    {{ norm('street_name') }} as street_name,
    {{ norm('community_board') }} as community_board
  from ranked where row_rank = 1
), keyed as (
  select *, cast(created_at as date) as event_date,
    {{ date_part('hour', 'created_at') }} as event_hour,
    {{ key(['borough', 'zip_code', 'street_name']) }} as location_key,
    {{ key(['complaint_type', 'descriptor']) }} as problem_key,
    {{ key(['borough', 'community_board']) }} as region_key
  from cleaned
)
select * from keyed
where agency = 'NYPD'
  and complaint_type in ('ILLEGAL PARKING', 'BLOCKED DRIVEWAY', 'ABANDONED VEHICLE', 'NOISE - VEHICLE', 'TRAFFIC')

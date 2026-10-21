-- A crash can have up to five reported vehicle slots. Do not SUM crash measures after joining this bridge.
select {{ key(['crash_id','vehicle_slot']) }} as crash_vehicle_key,
  crash_id, vehicle_slot,
  {{ key(['vehicle_type']) }} as vehicle_type_key,
  {{ key(['contributing_factor']) }} as contributing_factor_key
from {{ ref('int_crash_vehicle_slots') }}
where vehicle_type is not null or contributing_factor is not null

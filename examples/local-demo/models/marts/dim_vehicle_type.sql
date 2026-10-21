select distinct {{ key(['vehicle_type']) }} as vehicle_type_key, vehicle_type
from {{ ref('int_crash_vehicle_slots') }}

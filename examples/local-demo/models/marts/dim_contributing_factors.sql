select distinct {{ key(['contributing_factor']) }} as contributing_factor_key, contributing_factor
from {{ ref('int_crash_vehicle_slots') }}

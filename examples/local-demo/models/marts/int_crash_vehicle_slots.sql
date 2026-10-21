select crash_id, 1 as vehicle_slot, {{ norm('vehicle_type_code1') }} as vehicle_type, {{ norm('contributing_factor_vehicle_1') }} as contributing_factor
from {{ ref('stg_nyc_vehicle_crashes') }}
union all
select crash_id, 2 as vehicle_slot, {{ norm('vehicle_type_code2') }} as vehicle_type, {{ norm('contributing_factor_vehicle_2') }} as contributing_factor
from {{ ref('stg_nyc_vehicle_crashes') }}
union all
select crash_id, 3 as vehicle_slot, {{ norm('vehicle_type_code_3') }} as vehicle_type, {{ norm('contributing_factor_vehicle_3') }} as contributing_factor
from {{ ref('stg_nyc_vehicle_crashes') }}
union all
select crash_id, 4 as vehicle_slot, {{ norm('vehicle_type_code_4') }} as vehicle_type, {{ norm('contributing_factor_vehicle_4') }} as contributing_factor
from {{ ref('stg_nyc_vehicle_crashes') }}
union all
select crash_id, 5 as vehicle_slot, {{ norm('vehicle_type_code_5') }} as vehicle_type, {{ norm('contributing_factor_vehicle_5') }} as contributing_factor
from {{ ref('stg_nyc_vehicle_crashes') }}

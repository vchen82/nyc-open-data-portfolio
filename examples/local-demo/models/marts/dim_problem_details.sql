select distinct problem_key, complaint_type, descriptor
from {{ ref('stg_nyc_311_vehicle_complaints') }}

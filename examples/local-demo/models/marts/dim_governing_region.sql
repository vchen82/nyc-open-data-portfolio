select distinct region_key, borough, community_board
from {{ ref('stg_nyc_311_vehicle_complaints') }}

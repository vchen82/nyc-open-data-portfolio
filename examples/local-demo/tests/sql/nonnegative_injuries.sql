select * from {{ ref('fact_vehicle_crashes') }}
where persons_injured < 0 or persons_killed < 0 or pedestrians_injured < 0 or pedestrians_killed < 0 or cyclist_injured < 0 or cyclist_killed < 0 or motorist_injured < 0 or motorist_killed < 0

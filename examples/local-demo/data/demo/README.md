# Synthetic fixtures, not NYC observations

These deliberately small records exercise corrections, agency filtering, multiple vehicles, and missing ZIP codes. Street names are invented. Counts and ratios must not be presented as findings about New York City.

Expected results after staging: **7 complaints and 5 crashes**. Reporting excludes one missing-ZIP record from each source, giving **6 complaints and 4 crashes**. ZIP 10001 has 4 complaints, 3 crashes, and 2 pedestrian/cyclist injuries; ZIP 11373 has 2 complaints, 1 crash, and 1 pedestrian injury. Both injury ratios are suppressed by the default 20-parking-complaint threshold.

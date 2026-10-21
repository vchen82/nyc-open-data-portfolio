# Validation record

Validated locally on October 20, 2026, using Python 3.13, dbt-core 1.10.15, dbt-duckdb 1.9.6, and DuckDB 1.5.6.

| Check | Result |
| --- | --- |
| Offline dbt build | 17 models built successfully |
| dbt data tests | 43 passed |
| dbt metric unit test | 1 passed: threshold boundary, missing measures, and zero crashes |
| Python behavior and warehouse integration tests | 15 passed |
| dbt documentation and catalog generation | Passed |
| BigQuery adapter project parse | Passed using dbt-bigquery 1.9.2; no cloud execution |
| Source field validation | Selected columns matched the public Socrata metadata for both datasets |

The local demo confirms deduplication, source scope, corrected injury counts, non-inflating aggregate joins, exclusion and accounting of missing ZIPs, preservation of vehicle slots, small-denominator suppression, API retry decisions, and failure on incomplete paginated extracts.

Run the same local checks with:

```bash
python scripts/demo.py
```

GitHub Actions is configured to run this command on push and pull requests, using Python 3.12. A hosted Actions run has not yet occurred. The local validation was performed on macOS; other platforms are not claimed as tested.

## Not validated or deployed

- No Google Cloud resources were created, and no live records were loaded into BigQuery.
- BigQuery SQL has not been executed against a billing-enabled project. Project parsing validates configuration and references, not runtime SQL correctness or permissions.
- Cloud Functions, Scheduler authentication, quotas, and production retry behavior require deployment testing.
- An editable Looker Studio report definition is not bundled. The repository includes a dashboard setup guide and screenshot.
- Dashboard findings have not been independently verified with a full raw-data run of this repository.
- Check the top-level GitHub Actions page for the latest hosted validation status.

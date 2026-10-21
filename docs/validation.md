# Validation scope

## Main warehouse

The packaging checks compare every supplied archive file with its preserved copy by SHA-256 and verify that all dbt `ref()` calls resolve to models present in the project. This confirms preservation and model-reference completeness, not SQL execution correctness.

No main-warehouse models have been executed against BigQuery in this session. Credentials, existing raw datasets, deployment permissions, and the report's analytical queries were not available. No claim is made that all source tests pass in the cloud.

## Independent local demo

The example uses different model definitions. Its local run in this packaged folder built 17 models and passed 43 data tests, one metric unit test, and 15 Python tests. The packaged example is checked separately and must not be used as evidence that the main warehouse is tested.

GitHub Actions runs the source preservation check and the offline demo. Hosted CI runs begin after this repository is uploaded to GitHub.

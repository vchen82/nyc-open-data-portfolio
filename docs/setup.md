# Main warehouse setup

The main dbt project in `warehouse/` targets BigQuery and expects existing raw tables. The branch's SQL and configuration are preserved unchanged.

1. Create a Python environment and install `dbt-core==1.10.15` and `dbt-bigquery==1.9.2`.
2. Authenticate with Google Cloud Application Default Credentials and set `GCP_PROJECT_ID` to a project you can use.
3. Copy `config/profiles.example.yml` to a private `profiles.yml` outside the tracked source and point dbt at its containing directory using `--profiles-dir`.
4. Review both `sources.yml` files. They reference the class project and datasets explicitly; setting `GCP_PROJECT_ID` changes the execution project, not these source references. To use different raw tables, edit a working copy of the source definitions and supply the complete fields expected by the staging SQL.
5. From `warehouse/`, run `dbt deps`, then `dbt debug --profiles-dir /path/to/private-profile-folder`.
6. Build the vehicle project with `dbt build --select path:models/group_16_project --profiles-dir /path/to/private-profile-folder`.

Both source datasets must exist and be accessible. The source tables for the vehicle project are `source_nyc_311_vehicle_complaints` and `source_nyc_vehicle_crashes`. The group project's source schema is `group16_nyc_open_data_raw_dataset`.

The schema-name macro uses configured schema names directly: `nyc_crashes_complaints_staging` and `nyc_crashes_complaints_marts`. The target dataset does not isolate these destinations. Use a dedicated cloud project or deliberately change the configured schemas before a build if those datasets already contain work you need to preserve. Table materializations can replace existing model tables.

The unrelated restaurant/transit models are included under `assignment_work`; they require their own raw inputs. The group-only selection avoids building them. Source definitions and all SQL remain available for review.

## Items to review before a cloud run

- The crash staging date filter mixes a DATETIME expression with `DATE_SUB(CURRENT_DATETIME(), ...)`; validate and correct its BigQuery types if necessary.
- Ordinary casts can fail on malformed raw values. ZIP validation accepts some nonstandard values, and location dimensions exclude incomplete locations.
- The staging scope assumes the raw complaint table was already filtered to relevant NYPD complaints.
- Date filters are relative to the run date; they do not establish the original report's coverage window.
- Only source-ID tests are supplied in the branch. Add model-grain, relationship, and analytical reconciliation tests before treating outputs as validated.

These observations come from source inspection, not a successful BigQuery execution. The runnable example uses its own model definitions and tests; its test results do not validate this project.

## Supporting pipeline and demo

The extraction and loading code in `examples/local-demo/ingestion/` serves the example schema. Do not load its reduced raw schema and point the main project at it: the main staging models require additional columns, including fields used for governing region and request details. Adapting a loader for the main project requires matching the full source definitions and validating the loaded schema.

The example's cloud and dashboard guides document that example's tables. The main warehouse's ingestion functions and dashboard KPI queries are not present in the supplied archive; the main project should not be described as independently reproduced end-to-end until those components are supplied and tested.

# BigQuery and Cloud Functions setup

This path provisions resources in **your** Google Cloud project and may incur charges. The repository does not provision them automatically. Start with one day of data, inspect the manifests, and only then backfill larger windows.

## 1. Local credentials and dependencies

Install the Google Cloud CLI separately, select a billing-enabled project, and authenticate with Application Default Credentials. From the repository root in your virtual environment:

```bash
pip install -r requirements-cloud.txt
gcloud auth application-default login
export GCP_PROJECT_ID=your-project-id
export BQ_LOCATION=US
export BQ_RAW_DATASET=nyc_raw
export DBT_DATASET=nyc_analytics
```

Set `SOCRATA_APP_TOKEN` in your environment if available. The loader supports anonymous requests but the upstream service may throttle or require a token. Never place a token in committed configuration.

Enable the BigQuery API and give the operator permission to create datasets, write tables, and run jobs. Initialize raw storage:

```bash
python scripts/bootstrap_bigquery.py
```

The bootstrap preserves existing tables, including empty tables required when a date window yields no records. All source fields are deliberately loaded as strings; dbt handles conversions.

## 2. Fetch a complete, bounded window

```bash
python -m ingestion.pipeline --source complaints --start 2025-01-01 --end 2025-01-02 --output output/complaints.jsonl --load-bigquery
python -m ingestion.pipeline --source crashes --start 2025-01-01 --end 2025-01-02 --output output/crashes.jsonl --load-bigquery
```

Omit `--load-bigquery` to download only. Each successful CLI run writes a JSON manifest beside its output. Windows are start-inclusive and end-exclusive, limited to 31 days. The raw tables preserve all loaded windows and upsert by ID. Re-running a window updates existing records; it does not duplicate them. Run a single loader per source at a time. Concurrent overlapping loads are not a supported orchestration pattern.

The extractor uses ordered keyset pagination and retries transient errors. If the safety page limit is reached, it fails without replacing the previous output or loading a partial window. Use smaller windows rather than increasing the limit indiscriminately. A source can change while paging; historic records can be revised later. Keep manifests and re-fetch overlapping windows as needed.

## 3. Build the analytical warehouse

```bash
dbt debug --profiles-dir config --target bigquery
dbt build --profiles-dir config --target bigquery --vars '{"analysis_start":"2025-01-01","analysis_end":"2025-01-02"}'
```

Default dbt schema naming creates:

- `nyc_analytics_staging`
- `nyc_analytics_marts`
- `nyc_analytics_reporting`

The operator needs permission to create these datasets or have them created first, plus appropriate table and job permissions. All datasets must use a compatible location. The profile imposes a 10 GB bytes-billed limit per dbt query, not a total project budget. Initial table builds are full refreshes; start small. The raw merge is not subject to that dbt limit.

Verify both source manifests cover the analysis window before interpreting zeros. The warehouse does not automatically detect gaps in extraction coverage. Inspect `kpi_data_quality` and investigate failed data tests before sharing results.

## 4. Optional authenticated scheduled ingestion

Deploy `ingestion/` as a second-generation Python HTTP function with entry point `ingest`. Example for Google Cloud CLI; substitute your project, service account, and secret name:

```bash
gcloud functions deploy nyc-street-safety-ingest \
  --gen2 --runtime python312 --region us-central1 \
  --source ingestion --entry-point ingest --trigger-http \
  --no-allow-unauthenticated --timeout 540s --memory 512Mi \
  --max-instances 1 --concurrency 1 \
  --service-account nyc-ingest@YOUR_PROJECT.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT,BQ_RAW_DATASET=nyc_raw,BQ_LOCATION=US
```

Enable the Cloud Functions, Cloud Run, Cloud Build, Artifact Registry, and Cloud Scheduler APIs as required by your project. Create a dedicated runtime service account with BigQuery Job User on the project and Data Editor on the raw dataset. The deployer needs the appropriate deployment and service-account impersonation permissions. Use Secret Manager to provide `SOCRATA_APP_TOKEN` if required; do not pass a literal token in a command or commit it.

Create a dedicated Scheduler service account with Cloud Run Invoker on the deployed function's underlying Cloud Run service. Configure two HTTP POST jobs using OIDC authentication, the exact function URL as audience, and JSON bodies:

```json
{"source":"complaints"}
```

```json
{"source":"crashes"}
```

Set the schedule timezone to `America/New_York`; stagger the jobs (for example 02:00 and 02:30) and set the attempt deadline to 540 seconds. Monitor for timeouts and shrink the default seven-day lookback if necessary. An explicit backfill body can include `start` and `end`; do not leave a fixed historical window on a recurring job unintentionally.

Without explicit dates, the handler re-fetches the previous seven complete NYC calendar days. This captures recent revisions but not older changes or source deletions. A failure returns a non-success status so Scheduler can retry. The function writes no partial load if extraction hits its page cap. Set monitoring and budget alerts in your own project.

**Scheduler ingestion does not run dbt.** Run dbt only after both source jobs complete successfully, either manually or through a separately configured orchestrator/dbt job. A rolling operational dashboard also needs its analysis window updated. Scheduling ingestion alone does not create a continuously refreshed end-to-end dashboard.

## 5. Dashboard and future work

Follow [the dashboard guide](dashboard.md) after the BigQuery build succeeds. For full-history production operation, add coverage auditing, source-deletion reconciliation, partitioned/incremental models, incremental state management, and orchestration that gates reporting on successful ingestion.

# Scope and limitations

The repository provides a data warehouse, a synthetic local demo, a cloud ingestion pipeline, and a Looker Studio dashboard guide. Demo records are synthetic and must not be interpreted as NYC findings. Dashboard observations in the project report have not been independently verified with a full-data run of this repository.

## Analytical limitations

- Counts depend on source completeness, reporting behavior, record updates, and selected dates.
- Location fields can be missing or inconsistent; normalization is not geocoding validation.
- Busy/populous areas may generate more complaints and crashes without complaints being predictive.
- There are no traffic exposure denominators, population controls, lagged models, confidence intervals, or causal interventions here.
- A complaint-to-crash ratio can be unstable; low-volume injury ratios should not determine resource allocation on their own.
- The dashboard screenshot's labels are not evidence of a current refresh or a precise extraction cutoff.

## Operational limitations

The Python loader upserts IDs and captures recent revisions by re-fetching bounded windows. It does not reconcile source deletions or discover revisions older than the requested date window. Use periodic backfills and source reconciliation for a production pipeline. Keyset pagination is ordered but not a transactional snapshot of a changing upstream dataset.

BigQuery execution, IAM configuration, scheduled cloud invocations, and a live Looker dashboard require an account and separate validation. Passing the local demo does not prove those external integrations are deployed or working.

# Rebuild the Looker Studio dashboard

This repository includes analytical tables, queries, and a dashboard specification. It does not include an exportable Looker Studio report definition. A Google account and populated BigQuery target are required to create a live dashboard.

After a successful `dbt build --profiles-dir config --target bigquery`, connect Looker Studio to the generated reporting dataset (default `nyc_analytics_reporting`). Start with the same analysis window for every chart. Do not blend raw fact tables in Looker Studio.

| View | Table | Configuration |
| --- | --- | --- |
| Crash hotspots | `kpi_zip_summary` | Geography = ZIP; country = United States; color = crashes |
| Illegal parking vs. crashes by street | `kpi_daily_street` | Group by borough + ZIP + street; sum crashes and parking complaints; sort by crashes descending; top 20 |
| Chronological trends | `kpi_monthly_trends` | Sort year, then month; show complaints and crashes as separate, explicitly labeled series |
| Injury screening | `kpi_zip_summary` | Filter injury_ratio_eligible = true; display ZIP, vulnerable injuries, parking complaints, and the ratio |
| ZIP-level association | `kpi_zip_summary` | Scatter: X = complaints, Y = crashes, one point per ZIP |
| Data quality | `kpi_data_quality` | Show missing ZIP/street/date counts next to source totals |

`kpi_zip_summary` is pre-aggregated over the dbt window. Changing a Looker date filter will not recalculate it. Change dbt variables and rebuild for a new period, or design a separate date-aware aggregation from daily tables. If multiple ZIPs are combined, recompute ratios from totals.

Use descriptive labels and display the dataset cutoff date, selected window, source scope, and missing-location exclusions. Prefer separate panels over misleading dual axes. A street name by itself is not a unique citywide location.

The dashboard screenshot in `docs/assets/` is reference material only. It shows small denominator ratios and a ZIP/borough mismatch; do not use it as a validated current ranking. Results can differ with the window, refreshed source records, cleaning rules, and denominator threshold.

Before sharing: open the dashboard in a signed-out browser and confirm that intended viewers can access it. Choose data credentials and audience deliberately; never assume a BigQuery console link is a public dashboard.

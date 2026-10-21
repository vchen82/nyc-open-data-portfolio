"""Export generated demo tables; outputs are ignored by Git."""
import csv
import json
from pathlib import Path
import duckdb
root = Path(__file__).resolve().parents[1]
with duckdb.connect(str(root / 'output/warehouse.duckdb'), read_only=True) as con:
    for table in ['kpi_zip_summary', 'kpi_daily_street', 'kpi_monthly_trends', 'kpi_data_quality']:
        cur = con.execute(f'select * from analytics_reporting.{table}')
        cols = [x[0] for x in cur.description]
        rows = cur.fetchall()
        with (root / 'output' / (table + '.csv')).open('w', newline='') as stream:
            writer = csv.writer(stream); writer.writerow(cols); writer.writerows(rows)
        if table == 'kpi_zip_summary':
            summary = {'data_status': 'SYNTHETIC DEMO — NOT NYC FINDINGS', 'rows': [dict(zip(cols, row)) for row in rows]}
            (root / 'output/demo-summary.json').write_text(json.dumps(summary, indent=2, default=str) + '\n')

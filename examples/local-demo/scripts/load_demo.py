"""Load intentionally synthetic edge cases. Never downloads or overwrites cloud data."""
import json
from pathlib import Path
import sys
import duckdb
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ingestion.pipeline import SOURCES

def main():
    output = ROOT / 'output'
    output.mkdir(exist_ok=True)
    with duckdb.connect(str(output / 'warehouse.duckdb')) as con:
        con.execute('create schema if not exists raw')
        for source, spec in SOURCES.items():
            cols = spec['fields'] + ['_ingested_at']
            con.execute(f"create or replace table raw.{spec['table']} (" + ', '.join(f'"{c}" varchar' for c in cols) + ')')
            rows = json.loads((ROOT / 'data' / 'demo' / f'{source}.json').read_text())
            values = [[str(row[c]) if row.get(c) is not None else None for c in cols] for row in rows]
            con.executemany(f"insert into raw.{spec['table']} values (" + ','.join('?' for _ in cols) + ')', values)
            print(f'Loaded {len(rows)} SYNTHETIC {source} rows')

if __name__ == '__main__':
    main()

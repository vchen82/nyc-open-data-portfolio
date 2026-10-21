"""Bounded Socrata extraction; complete downloads are merged into BigQuery by ID."""
from __future__ import annotations
import argparse
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import uuid

COMPLAINT_TYPES = ('Illegal Parking', 'Blocked Driveway', 'Abandoned Vehicle', 'Noise - Vehicle', 'Traffic')
COMPLAINT_FIELDS = 'unique_key created_date closed_date agency complaint_type descriptor status borough incident_zip street_name community_board latitude longitude'.split()
CRASH_FIELDS = ('collision_id crash_date crash_time borough zip_code on_street_name latitude longitude '
                'number_of_persons_injured number_of_persons_killed number_of_pedestrians_injured '
                'number_of_pedestrians_killed number_of_cyclist_injured number_of_cyclist_killed '
                'number_of_motorist_injured number_of_motorist_killed').split()
CRASH_FIELDS += [f'contributing_factor_vehicle_{i}' for i in range(1, 6)]
CRASH_FIELDS += ['vehicle_type_code1', 'vehicle_type_code2', 'vehicle_type_code_3', 'vehicle_type_code_4', 'vehicle_type_code_5']
SOURCES = {
    'complaints': {'dataset': 'erm2-nwe9', 'id': 'unique_key', 'date': 'created_date', 'fields': COMPLAINT_FIELDS, 'table': 'source_nyc_311_vehicle_complaints'},
    'crashes': {'dataset': 'h9gi-nx95', 'id': 'collision_id', 'date': 'crash_date', 'fields': CRASH_FIELDS, 'table': 'source_nyc_vehicle_crashes'},
}

def validate_window(start, end):
    a, b = date.fromisoformat(start), date.fromisoformat(end)
    if not 0 < (b - a).days <= 31:
        raise ValueError('Use a nonempty window of at most 31 days; end is exclusive.')
    if a < date(2020, 1, 1):
        raise ValueError('This pipeline targets the 2020-present 311 dataset.')
    return a.isoformat(), b.isoformat()

def query_parameters(source, start, end, cursor=None, page_size=10000):
    start, end = validate_window(start, end)
    if not 1 <= page_size <= 50000:
        raise ValueError('page_size must be 1..50000')
    spec = SOURCES[source]
    where = f"{spec['date']} >= '{start}T00:00:00' AND {spec['date']} < '{end}T00:00:00'"
    if source == 'complaints':
        categories = ','.join("'" + c + "'" for c in COMPLAINT_TYPES)
        where += f" AND agency = 'NYPD' AND complaint_type IN ({categories})"
    if cursor is not None:
        # Both sources use digit-only IDs. 311 is text, collisions are numeric.
        if not re.fullmatch(r'[0-9]+', str(cursor)):
            raise ValueError('Unexpected source ID format')
        literal = f"'{cursor}'" if source == 'complaints' else str(cursor)
        where += f" AND {spec['id']} > {literal}"
    return {'$select': ','.join(spec['fields']), '$where': where,
            '$order': spec['id'] + ' ASC', '$limit': str(page_size)}

def fetch_page(source, params, attempts=5):
    url = f"https://data.cityofnewyork.us/resource/{SOURCES[source]['dataset']}.json?{urlencode(params)}"
    headers = {'Accept': 'application/json', 'User-Agent': 'nyc-street-safety-portfolio/1.0'}
    if os.getenv('SOCRATA_APP_TOKEN'):
        headers['X-App-Token'] = os.environ['SOCRATA_APP_TOKEN']
    for attempt in range(attempts):
        try:
            with urlopen(Request(url, headers=headers), timeout=60) as response:
                rows = json.load(response)
            if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
                raise ValueError('Expected a list of Socrata records')
            return rows
        except (HTTPError, URLError, TimeoutError) as exc:
            retryable = not isinstance(exc, HTTPError) or exc.code in (429, 500, 502, 503, 504)
            if not retryable or attempt == attempts - 1:
                raise
            time.sleep(min(2 ** attempt, 30))

def extract(source, start, end, destination, page_size=10000, max_pages=100, fetch=fetch_page):
    """Write NDJSON only on success. Stable keyset paging avoids OFFSET drift."""
    validate_window(start, end)
    if max_pages < 1:
        raise ValueError('max_pages must be positive')
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    staged = destination.with_name(destination.name + '.' + uuid.uuid4().hex + '.partial')
    cursor, count = None, 0
    spec = SOURCES[source]
    ingested = datetime.now(timezone.utc).isoformat()
    try:
        with staged.open('w') as stream:
            for _ in range(max_pages):
                rows = fetch(source, query_parameters(source, start, end, cursor, page_size))
                for row in rows:
                    current = str(row.get(spec['id'], ''))
                    if not re.fullmatch(r'[0-9]+', current):
                        raise ValueError('Missing or invalid source ID')
                    key = current if source == 'complaints' else int(current)
                    prior = cursor if source == 'complaints' else int(cursor) if cursor is not None else None
                    if prior is not None and key <= prior:
                        raise ValueError('Source IDs are not strictly increasing')
                    cursor = current
                    clean = {field: str(row[field]) if row.get(field) is not None else None for field in spec['fields']}
                    clean['_ingested_at'] = ingested
                    stream.write(json.dumps(clean) + '\n')
                    count += 1
                if len(rows) < page_size:
                    break
            else:
                raise RuntimeError('Page limit reached; no output committed. Use a smaller date window.')
        staged.replace(destination)
    finally:
        staged.unlink(missing_ok=True)
    return {'source': source, 'dataset_id': spec['dataset'], 'start': start, 'end_exclusive': end,
            'rows': count, 'extracted_at': ingested}

def merge_bigquery(source, path, project, dataset, location='US'):
    """Temporary load + one MERGE. Retries update IDs rather than duplicate them."""
    from google.cloud import bigquery
    from datetime import timedelta
    if not re.fullmatch(r'[a-z][a-z0-9-]{4,61}[a-z0-9]', project):
        raise ValueError('Invalid Google Cloud project ID')
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', dataset):
        raise ValueError('Invalid BigQuery dataset')
    if Path(path).stat().st_size == 0:
        return 0
    client = bigquery.Client(project=project, location=location)
    spec = SOURCES[source]
    cols = spec['fields'] + ['_ingested_at']
    schema = [bigquery.SchemaField(c, 'STRING') for c in cols]
    destination = f"{project}.{dataset}.{spec['table']}"
    client.create_table(bigquery.Table(destination, schema=schema), exists_ok=True)
    temp_id = f'{project}.{dataset}._load_{uuid.uuid4().hex}'
    table = bigquery.Table(temp_id, schema=schema)
    table.expires = datetime.now(timezone.utc) + timedelta(hours=6)
    client.create_table(table)
    try:
        config = bigquery.LoadJobConfig(schema=schema, source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON)
        with open(path, 'rb') as stream:
            loaded = client.load_table_from_file(stream, temp_id, job_config=config).result()
        assignments = ', '.join(f'T.`{c}` = S.`{c}`' for c in cols)
        names = ', '.join(f'`{c}`' for c in cols)
        values = ', '.join(f'S.`{c}`' for c in cols)
        sql = f"""MERGE `{destination}` T USING `{temp_id}` S
        ON T.`{spec['id']}` = S.`{spec['id']}`
        WHEN MATCHED AND S._ingested_at >= COALESCE(T._ingested_at, '') THEN UPDATE SET {assignments}
        WHEN NOT MATCHED THEN INSERT ({names}) VALUES ({values})"""
        client.query(sql).result()
        return loaded.output_rows
    finally:
        client.delete_table(temp_id, not_found_ok=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', choices=SOURCES, required=True)
    parser.add_argument('--start', required=True)
    parser.add_argument('--end', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--load-bigquery', action='store_true')
    args = parser.parse_args()
    result = extract(args.source, args.start, args.end, args.output)
    if args.load_bigquery:
        result['loaded_rows'] = merge_bigquery(args.source, args.output, os.environ['GCP_PROJECT_ID'], os.getenv('BQ_RAW_DATASET', 'nyc_raw'), os.getenv('BQ_LOCATION', 'US'))
    Path(args.output + '.manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()

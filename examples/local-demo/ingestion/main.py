"""Authenticated HTTP entry point for Cloud Functions (2nd generation)."""
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import tempfile
from zoneinfo import ZoneInfo
import functions_framework
try:
    from .pipeline import SOURCES, extract, merge_bigquery, validate_window
except ImportError:
    from pipeline import SOURCES, extract, merge_bigquery, validate_window

@functions_framework.http
def ingest(request):
    if request.method != 'POST':
        return ('POST required', 405)
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return ('JSON object required', 400)
    try:
        source = body.get('source')
        if source not in SOURCES:
            raise ValueError('source must be complaints or crashes')
        if ('start' in body) != ('end' in body):
            raise ValueError('Provide both start and end, or neither')
        # Re-fetch seven complete local calendar days to capture recent revisions.
        today = datetime.now(ZoneInfo('America/New_York')).date()
        start = body.get('start', (today - timedelta(days=7)).isoformat())
        end = body.get('end', today.isoformat())
        validate_window(start, end)
    except (TypeError, ValueError) as exc:
        return (str(exc), 400)
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'batch.jsonl'
        result = extract(source, start, end, path, max_pages=20)
        result['loaded_rows'] = merge_bigquery(source, path, os.environ['GCP_PROJECT_ID'], os.getenv('BQ_RAW_DATASET', 'nyc_raw'), os.getenv('BQ_LOCATION', 'US'))
    # Extraction/loading failures deliberately propagate as 5xx so Scheduler can retry.
    return (json.dumps(result), 200, {'Content-Type': 'application/json'})

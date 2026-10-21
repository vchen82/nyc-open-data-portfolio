"""Create the raw dataset/tables using Application Default Credentials."""
import os
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from google.cloud import bigquery
from ingestion.pipeline import SOURCES
project=os.environ['GCP_PROJECT_ID']
raw=os.getenv('BQ_RAW_DATASET','nyc_raw')
location=os.getenv('BQ_LOCATION','US')
if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',raw):
    raise ValueError('Invalid raw dataset name')
client=bigquery.Client(project=project,location=location)
dataset=bigquery.Dataset(f'{project}.{raw}')
dataset.location=location
client.create_dataset(dataset,exists_ok=True)
for spec in SOURCES.values():
    schema=[bigquery.SchemaField(c,'STRING') for c in spec['fields']+['_ingested_at']]
    client.create_table(bigquery.Table(f"{project}.{raw}.{spec['table']}",schema=schema),exists_ok=True)
print('Raw dataset and tables ready. Existing tables were preserved.')

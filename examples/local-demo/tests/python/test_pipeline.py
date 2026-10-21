import json
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
import pytest
from ingestion.pipeline import extract, query_parameters, validate_window, fetch_page

@pytest.mark.parametrize('a,b', [('2025-01-02','2025-01-01'),('2025-01-01','2025-01-01'),('2025-01-01','2025-03-01'),('2019-01-01','2019-01-02')])
def test_invalid_windows(a,b):
    with pytest.raises(ValueError): validate_window(a,b)

def test_filters_and_cursor_types():
    p = query_parameters('complaints','2025-01-01','2025-01-02','9')
    assert "unique_key > '9'" in p['$where']
    assert "agency = 'NYPD'" in p['$where']
    assert "< '2025-01-02T00:00:00'" in p['$where']
    assert 'collision_id > 9' in query_parameters('crashes','2025-01-01','2025-01-02','9')['$where']

def test_keyset_pagination_and_null_fields(tmp_path):
    calls=[]
    def fetch(source, params):
        calls.append(params)
        return [{'collision_id':'2'},{'collision_id':'10'}] if len(calls)==1 else [{'collision_id':'11'}]
    dest=tmp_path/'data.jsonl'
    result=extract('crashes','2025-01-01','2025-01-02',dest,page_size=2,fetch=fetch)
    assert result['rows']==3
    assert 'collision_id > 10' in calls[1]['$where']
    assert json.loads(dest.read_text().splitlines()[0])['zip_code'] is None

def test_page_cap_preserves_previous_output(tmp_path):
    dest=tmp_path/'data.jsonl'; dest.write_text('previous')
    with pytest.raises(RuntimeError):
        extract('crashes','2025-01-01','2025-01-02',dest,page_size=1,max_pages=1,fetch=lambda *_:[{'collision_id':'1'}])
    assert dest.read_text()=='previous'
    assert list(tmp_path.glob('*.partial'))==[]

def test_repeated_id_fails_without_publishing(tmp_path):
    with pytest.raises(ValueError,match='strictly increasing'):
        extract('crashes','2025-01-01','2025-01-02',tmp_path/'x',fetch=lambda *_:[{'collision_id':'1'},{'collision_id':'1'}])
    assert not (tmp_path/'x').exists()

def test_http_429_retries():
    response=__import__('io').BytesIO(b'[]')
    with patch('ingestion.pipeline.urlopen',side_effect=[HTTPError('url',429,'rate limit',{},None),response]) as opener, patch('ingestion.pipeline.time.sleep'):
        assert fetch_page('crashes',{})==[]
    assert opener.call_count==2

def test_http_400_does_not_retry():
    with patch('ingestion.pipeline.urlopen',side_effect=HTTPError('url',400,'bad query',{},None)) as opener:
        with pytest.raises(HTTPError): fetch_page('crashes',{})
    assert opener.call_count==1

from pathlib import Path
import duckdb
import pytest

@pytest.fixture
def db():
    path=Path('output/warehouse.duckdb')
    if not path.exists(): pytest.skip('Run python scripts/demo.py for warehouse integration tests')
    with duckdb.connect(str(path),read_only=True) as con:
        yield con

def test_deduplication_and_scope(db):
    assert db.execute('select count(*) from analytics_marts.fact_311_vehicle_complaints').fetchone()[0]==7
    assert db.execute('select count(*) from analytics_marts.fact_vehicle_crashes').fetchone()[0]==5
    assert db.execute("select status from analytics_marts.fact_311_vehicle_complaints where complaint_id='1'").fetchone()[0]=='Closed'.upper()

def test_no_join_fanout_and_corrected_injuries(db):
    row=db.execute("select complaints, crashes, vulnerable_injuries from analytics_reporting.kpi_zip_summary where zip_code='10001'").fetchone()
    assert row==(4,3,2)
    assert db.execute('select sum(complaints),sum(crashes) from analytics_reporting.kpi_zip_summary').fetchone()==(6,4)

def test_small_denominator_suppression(db):
    assert db.execute('select count(*) from analytics_reporting.kpi_zip_summary where vulnerable_injuries_per_parking_complaint is not null').fetchone()[0]==0

def test_missing_locations_are_visible(db):
    assert db.execute('select sum(missing_zip) from analytics_reporting.kpi_data_quality').fetchone()[0]==2

def test_vehicle_slots_dont_change_fact_grain(db):
    assert db.execute("select count(*) from analytics_marts.bridge_crash_vehicles where crash_id='1'").fetchone()[0]==2
    assert db.execute("select count(*) from analytics_marts.fact_vehicle_crashes where crash_id='1'").fetchone()[0]==1

"""Run the complete offline demo from any working directory."""
from pathlib import Path
import os
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
env = dict(os.environ, DBT_SEND_ANONYMOUS_USAGE_STATS='false')
for command in [
    [sys.executable, 'scripts/load_demo.py'],
    [str(Path(sys.executable).parent / ('dbt.exe' if os.name == 'nt' else 'dbt')), 'build', '--profiles-dir', 'config', '--target', 'demo'],
    [sys.executable, '-m', 'pytest', 'tests/python', '-q'],
    [sys.executable, 'scripts/export_demo.py'],
]:
    subprocess.run(command, cwd=ROOT, env=env, check=True)
print('Done. SYNTHETIC results: output/demo-summary.json and output/*.csv')

"""Verify archive preservation and internal dbt model references without cloud access."""
from pathlib import Path
import hashlib
import json
import re
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'docs/source-files.sha256.json').read_text())
for path,expected in manifest.items():
    assert hashlib.sha256((root/path).read_bytes()).hexdigest()==expected, path
models=list((root/'warehouse/models').rglob('*.sql'))
names=[p.stem for p in models]
assert len(names)==len(set(names)), 'Duplicate model names'
for path in models:
    for name in re.findall(r"ref\(['\"]([^'\"]+)['\"]\)",path.read_text()):
        assert name in names, (str(path),name)
print(f'Preserved {len(manifest)} source files; references resolve across {len(models)} SQL models.')

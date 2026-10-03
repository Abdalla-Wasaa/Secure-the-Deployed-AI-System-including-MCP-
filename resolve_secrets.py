import os
import yaml
from pathlib import Path
ROOT = Path(__file__).parent

def resolve_secrets():
    refs = yaml.safe_load((ROOT/'secret_refs.yaml').read_text())
    resolved = {}
    for name, ref in refs.items():
        value = os.environ.get(ref['env'], '')
        if len(value.encode()) < 32 or not value.strip():
            raise RuntimeError(f'{name} missing or shorter than 32 bytes')
        resolved[name] = value
    return resolved

if __name__ == '__main__':
    try:
        values = resolve_secrets()
        print('Resolved references: ' + ', '.join(sorted(values)))
    except RuntimeError as exc:
        print(str(exc)); raise SystemExit(1)

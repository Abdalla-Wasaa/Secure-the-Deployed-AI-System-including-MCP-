"""Redact sensitive shapes first; hash only the resulting text."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
PATTERNS = [r'(?i)bearer\s+[^\s,;]+', r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b', r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', r'(?<!\w)\+?\d[\d ()-]{5,}\d(?!\w)']
def redact(text):
    for pattern in PATTERNS:
        text = re.sub(pattern, '[REDACTED]', str(text))
    return text

def redact_then_hash(text):
    cleaned = redact(text)
    return {'redacted':cleaned, 'sha256':hashlib.sha256(cleaned.encode()).hexdigest()}

def write_audit(path, *, actor, action, resource, outcome, trace_id):
    # Hash identifiers after redaction; never retain arbitrary input text.
    row = {'actor':redact_then_hash(actor)['sha256'], 'resource':redact_then_hash(resource)['sha256'],
           'action':action if action in {'triage','check_stock','plan_delivery_route','rights','request'} else 'request',
           'outcome':outcome if outcome in {'allowed','denied','error','deleted'} else 'error',
           'trace_id':hashlib.sha256(str(trace_id).encode()).hexdigest(),
           'timestamp':datetime.now(timezone.utc).isoformat()}
    dest=Path(path); dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('a') as stream: stream.write(json.dumps(row)+'\n')
    return row

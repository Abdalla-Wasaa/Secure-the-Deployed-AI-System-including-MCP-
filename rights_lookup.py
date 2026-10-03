"""Local rights-owner workflow; use only after identity and authority verification."""
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path

def subject_key(subject):
    secret=os.environ.get('SUBJECT_PEPPER','')
    if len(secret.encode()) < 32: raise RuntimeError('SUBJECT_PEPPER required (32 bytes minimum)')
    return hmac.new(secret.encode(),subject.encode(),hashlib.sha256).hexdigest()

def access(subject, data_path, *, verified=False):
    if not verified: raise PermissionError('Rights owner must verify requester identity and authority')
    wanted=subject_key(subject)
    return [r for r in json.loads(Path(data_path).read_text()) if r['subject_hash']==wanted]

def erase(subject,data_path,deletion_path, *, verified=False):
    if not verified: raise PermissionError('Rights owner must verify requester identity and authority')
    if Path(data_path).resolve()==Path(deletion_path).resolve(): raise ValueError('Deletion ledger protected')
    rows=json.loads(Path(data_path).read_text()); wanted=subject_key(subject)
    kept=[r for r in rows if r['subject_hash']!=wanted]
    # Record intent first: a failed data write cannot silently erase without evidence.
    row={'subject_hash':wanted,'count':len(rows)-len(kept),'timestamp':datetime.now(timezone.utc).isoformat(),'status':'requested'}
    with Path(deletion_path).open('a') as stream: stream.write(json.dumps(row)+'\n')
    temp=Path(str(data_path)+'.tmp'); temp.write_text(json.dumps(kept)); temp.replace(data_path)
    row['status']='completed'
    with Path(deletion_path).open('a') as stream: stream.write(json.dumps(row)+'\n')
    return row

import os
import secrets
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from redact_then_hash import write_audit
checks=[('HTTPS pass',[sys.executable,'transit_policy.py','https://api.afyaplus.ke'],0),('HTTP production denial',[sys.executable,'transit_policy.py','http://api.afyaplus.ke'],1),('Lab loopback',[sys.executable,'transit_policy.py','--lab','http://localhost:8000'],0)]
env=os.environ.copy(); env.pop('JWT_SECRET',None); env.pop('SUBJECT_PEPPER',None)
r=subprocess.run([sys.executable,'resolve_secrets.py'],cwd=ROOT,env=env,capture_output=True,text=True)
assert r.returncode==1
lines=['Missing-secret failure: exit 1; '+r.stdout.strip()]
for title,cmd,expected in checks:
 r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True); assert r.returncode==expected
 lines.append(f'{title}: exit {r.returncode}; {r.stdout.strip()}')
env.update(JWT_SECRET=secrets.token_hex(32),SUBJECT_PEPPER=secrets.token_hex(32))
r=subprocess.run([sys.executable,'resolve_secrets.py'],cwd=ROOT,env=env,capture_output=True,text=True); assert r.returncode==0
lines.append(r.stdout.strip())
(ROOT/'docs/audit_sample.jsonl').write_text('')
write_audit(ROOT/'docs/audit_sample.jsonl',actor='synthetic-partner',action='triage',resource='synthetic-clinic',outcome='allowed',trace_id='synthetic-trace')
(ROOT/'docs/evidence.txt').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))

import tempfile
import json
from rights_lookup import subject_key, access, erase
os.environ['SUBJECT_PEPPER']=secrets.token_hex(32)
with tempfile.TemporaryDirectory() as temp:
    store=Path(temp)/'subjects.json'
    ledger=Path(temp)/'deletion_records.jsonl'; ledger.write_text('')
    store.write_text(json.dumps([{'subject_hash':subject_key('synthetic-subject'),'message':'synthetic fixture'}]))
    assert len(access('synthetic-subject',store,verified=True))==1
    assert erase('synthetic-subject',store,ledger,verified=True)['count']==1
    assert access('synthetic-subject',store,verified=True)==[]
    # Publish synthetic deletion evidence only, never the disposable pepper.
    (ROOT/'docs/deletion_sample.jsonl').write_text(ledger.read_text())

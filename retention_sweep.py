import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

def sweep(path, category, ledger, now=None):
    policy=json.loads((Path(__file__).parent/'retention.json').read_text())
    if category=='deletion_records' or Path(path).name=='deletion_records.jsonl' or Path(path).resolve()==Path(ledger).resolve():
        raise ValueError('Deletion records must never be swept')
    days=policy[category]['days']; cutoff=(now or datetime.now(timezone.utc))-timedelta(days=days)
    rows=[json.loads(line) for line in Path(path).read_text().splitlines() if line]
    kept=[r for r in rows if datetime.fromisoformat(r['timestamp']) >= cutoff]
    record={'category':category,'count':len(rows)-len(kept),'timestamp':(now or datetime.now(timezone.utc)).isoformat(),'status':'requested'}
    with Path(ledger).open('a') as stream: stream.write(json.dumps(record)+'\n')
    temp=Path(str(path)+'.tmp'); temp.write_text(''.join(json.dumps(r)+'\n' for r in kept)); temp.replace(path)
    record['status']='completed'
    with Path(ledger).open('a') as stream: stream.write(json.dumps(record)+'\n')
    return record

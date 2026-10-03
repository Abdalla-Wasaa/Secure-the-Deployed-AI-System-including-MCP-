import json
import secrets
from datetime import datetime,timezone
import pytest
from rights_lookup import subject_key,access,erase
from retention_sweep import sweep

def test_rights(tmp_path,monkeypatch):
    monkeypatch.setenv('SUBJECT_PEPPER',secrets.token_hex(32))
    path=tmp_path/'subjects.json'; ledger=tmp_path/'deletion_records.jsonl'; ledger.write_text('')
    path.write_text(json.dumps([{'subject_hash':subject_key('synthetic-a'),'data':'fixture'},{'subject_hash':subject_key('synthetic-b'),'data':'other'}]))
    with pytest.raises(PermissionError): access('synthetic-a',path)
    assert len(access('synthetic-a',path,verified=True))==1
    with pytest.raises(PermissionError): erase('synthetic-a',path,ledger)
    assert erase('synthetic-a',path,ledger,verified=True)['count']==1
    assert access('synthetic-a',path,verified=True)==[]
    assert len(access('synthetic-b',path,verified=True))==1
    assert 'synthetic-a' not in ledger.read_text()
    assert len(ledger.read_text().splitlines())==2

def test_sweep(tmp_path):
    path=tmp_path/'audit.jsonl'; ledger=tmp_path/'deletion_records.jsonl'; ledger.write_text('')
    path.write_text(json.dumps({'timestamp':'2000-01-01T00:00:00+00:00'})+'\n'+json.dumps({'timestamp':'2026-10-01T00:00:00+00:00'})+'\n')
    assert sweep(path,'audit_logs',ledger,datetime(2026,10,3,tzinfo=timezone.utc))['count']==1
    original=ledger.read_text()
    with pytest.raises(ValueError): sweep(ledger,'audit_logs',ledger)
    with pytest.raises(ValueError): sweep(path,'deletion_records',ledger)
    assert ledger.read_text()==original

import json
from redact_then_hash import redact_then_hash,write_audit

def test_redaction():
    text='ID 87654321 phone +254 712 345 678 email test@example.com Bearer eyJ.demo.token'
    row=redact_then_hash(text)
    for value in ['87654321','712','test@example.com','eyJ.demo.token']: assert value not in row['redacted']
    assert len(row['sha256'])==64
    assert redact_then_hash(text)==row

def test_all_fields(tmp_path):
    sensitive='Bearer private-token test@example.com 87654321'
    path=tmp_path/'audit.jsonl'
    row=write_audit(path,actor=sensitive,resource=sensitive,action=sensitive,outcome=sensitive,trace_id=sensitive)
    assert set(['actor','action','resource','outcome','trace_id']) <= row.keys()
    assert 'private-token' not in path.read_text()
    assert 'test@example.com' not in path.read_text()
    assert '87654321' not in path.read_text()

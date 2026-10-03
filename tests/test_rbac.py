import pytest
from rbac import allowed
@pytest.mark.parametrize('role',['unknown','invented',''])
def test_unknown(role):
    for action in ['triage','check_stock','plan_delivery_route','rights']: assert not allowed(role,action)
def test_least_privilege():
    assert allowed('partner','triage')
    assert not allowed('partner','plan_delivery_route')
    assert not allowed('operations','triage')
    assert not allowed('admin','dump_environment')
def test_api_auth(client,token):
    body={'message':'Fever','clinic_id':'KSM-01'}
    assert client.post('/triage',json=body).status_code==401
    assert client.post('/triage',headers={'Authorization':'Bearer invalid'},json=body).status_code==401
    assert client.post('/triage',headers=token(expired=True),json=body).status_code==401
    assert client.post('/triage',headers=token('unknown'),json=body).status_code==403
    assert client.post('/triage',headers=token(),json=body).status_code==200
    body['clinic_id']='VIH-01'
    assert client.post('/triage',headers=token(),json=body).status_code==403
    body['clinic_id']='EVIL-01'
    assert client.post('/triage',headers=token(clinics=['EVIL-01']),json=body).status_code==403
def test_mcp(client,token):
    body={'id':1,'method':'tools/call','params':{'name':'check_stock','arguments':{'clinic_id':'KSM-01'}}}
    assert client.post('/mcp',json=body).status_code==401
    response=client.post('/mcp',headers=token(),json=body)
    assert response.status_code==200
    assert 'environment' not in response.text and 'VIH-01' not in response.text
    body['params']['name']='plan_delivery_route'
    assert client.post('/mcp',headers=token(),json=body).status_code==403
    assert client.post('/mcp',headers=token('operations'),json=body).status_code==200
    body['params']['arguments']['clinic_id']='VIH-01'
    assert client.post('/mcp',headers=token('admin'),json=body).status_code==403
    assert client.post('/mcp',headers=token('unknown'),json={'id':1,'method':'tools/list'}).status_code==403

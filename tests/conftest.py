import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import secrets
import time
import jwt
import pytest
from app import app
@pytest.fixture
def client(monkeypatch,tmp_path):
    import asyncio
    import httpx
    monkeypatch.setenv('JWT_SECRET',secrets.token_hex(32))
    monkeypatch.setenv('SUBJECT_PEPPER',secrets.token_hex(32))
    monkeypatch.setenv('AUDIT_PATH',str(tmp_path/'audit.jsonl'))
    class Client:
        def post(self,path,**kwargs):
            async def invoke():
                async with app.router.lifespan_context(app):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test') as c:
                        return await c.post(path,**kwargs)
            return asyncio.run(invoke())
    from resolve_secrets import resolve_secrets
    app.state.secrets=resolve_secrets()
    yield Client()
@pytest.fixture
def token(client):
    def make(role='partner',clinics=None,expired=False):
        now=int(time.time())
        claims={'sub':'synthetic-user','role':role,'clinics':clinics if clinics is not None else ['KSM-01'],'iss':'afyaplus-auth','aud':'afyaplus','iat':now-120,'exp':now-1 if expired else now+300}
        return {'Authorization':'Bearer '+jwt.encode(claims,app.state.secrets['JWT_SECRET'],algorithm='HS256')}
    return make

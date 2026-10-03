import pytest
from transit_policy import transit_ok
from resolve_secrets import resolve_secrets
@pytest.mark.parametrize('url',['http://api.afyaplus.ke','ftp://localhost','https://user:pass@example.com','https:///bad','http://localhost.evil','https://example.com:bad'])
def test_denied(url): assert not transit_ok(url)
def test_pass():
    assert transit_ok('https://example.com')
    assert transit_ok('http://localhost:8000',True)
    assert not transit_ok('http://localhost:8000')
def test_missing_secret(monkeypatch):
    monkeypatch.delenv('JWT_SECRET',raising=False)
    with pytest.raises(RuntimeError): resolve_secrets()
def test_boot_fail_closed(monkeypatch):
    from app import app
    import asyncio
    monkeypatch.delenv('JWT_SECRET',raising=False)
    with pytest.raises(RuntimeError):
        async def boot():
            async with app.router.lifespan_context(app): pass
        asyncio.run(boot())


def test_startup_rejects_production_http(monkeypatch):
    import asyncio
    import secrets
    from app import app
    monkeypatch.setenv('JWT_SECRET',secrets.token_hex(32))
    monkeypatch.setenv('SUBJECT_PEPPER',secrets.token_hex(32))
    monkeypatch.setenv('PARTNER_URL','http://api.afyaplus.ke')
    monkeypatch.setenv('APP_ENV','production')
    async def boot():
        async with app.router.lifespan_context(app): pass
    with pytest.raises(RuntimeError): asyncio.run(boot())

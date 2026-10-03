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

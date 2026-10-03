import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
import jwt
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from resolve_secrets import resolve_secrets
from transit_policy import transit_ok
from injection_guard import guard
from rbac import allowed
from mcp_server import call_tool, TOOLS
from redact_then_hash import write_audit

@asynccontextmanager
async def lifespan(app):
    app.state.secrets = resolve_secrets()
    if not transit_ok(os.getenv('PARTNER_URL','https://api.afyaplus.ke'), os.getenv('APP_ENV') == 'lab'):
        raise RuntimeError('Partner URL violates transit policy')
    yield

app = FastAPI(lifespan=lifespan)
bearer = HTTPBearer(auto_error=False)
async def principal(request: Request, credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    if credentials is None: raise HTTPException(401,'JWT required', headers={'WWW-Authenticate':'Bearer'})
    try:
        claims=jwt.decode(credentials.credentials, request.app.state.secrets['JWT_SECRET'], algorithms=['HS256'], audience='afyaplus',issuer='afyaplus-auth',options={'require':['exp','iat','sub','role','clinics']})
        if not isinstance(claims['sub'],str) or not isinstance(claims['role'],str) or not isinstance(claims['clinics'],list) or not all(isinstance(c,str) for c in claims['clinics']): raise ValueError()
        request.state.actor=claims['sub']
        return claims
    except (jwt.PyJWTError,ValueError,TypeError):
        raise HTTPException(401,'Invalid JWT', headers={'WWW-Authenticate':'Bearer'})

@app.middleware('http')
async def audit(request, next_handler):
    trace=uuid.uuid4().hex
    response=await next_handler(request)
    write_audit(Path(os.getenv('AUDIT_PATH',str(Path(__file__).parent/'runtime/audit_log.jsonl'))),actor=getattr(request.state,'actor','anonymous'), action='request', resource=request.url.path, outcome='allowed' if response.status_code < 400 else 'denied',trace_id=trace)
    response.headers['X-Trace-ID']=trace
    return response

class Triage(BaseModel):
    message: str = Field(min_length=1,max_length=4000)
    clinic_id: str

def model_recommendation(message):
    return 'Contact a qualified clinician for assessment.'

@app.post('/triage')
async def triage(body:Triage, user=Depends(principal)):
    guard(body.message)
    if not allowed(user['role'],'triage'): raise HTTPException(403,'Role denied')
    stock=call_tool(user,'check_stock',body.clinic_id,body.message)
    return {'recommendation':model_recommendation(body.message),'human_review_required':True,'clinic_id':stock['clinic_id'],'source':'lab_stub'}

class RPC(BaseModel):
    jsonrpc: str = '2.0'
    id: int | str
    method: str
    params: dict = Field(default_factory=dict)

@app.post('/mcp')
async def mcp(body:RPC,user=Depends(principal)):
    if body.jsonrpc != '2.0': raise HTTPException(400,'Invalid JSON-RPC version')
    if body.method == 'initialize':
        if not any(allowed(user['role'], t) for t in TOOLS): raise HTTPException(403,'Role denied')
        result={'protocolVersion':'2025-03-26','capabilities':{'tools':{}},'serverInfo':{'name':'afyaplus-lab','version':'1.0.0'}}
    elif body.method == 'tools/list':
        if not any(allowed(user['role'], t) for t in TOOLS): raise HTTPException(403,'Role denied')
        result={'tools':[{'name':name,'description':'Clinic-scoped lab tool','inputSchema':{'type':'object','properties':{'clinic_id':{'type':'string'},'query':{'type':'string'}},'required':['clinic_id'],'additionalProperties':False}} for name in sorted(TOOLS) if allowed(user['role'],name)]}
    elif body.method == 'tools/call':
        if not isinstance(body.params.get('name'),str): raise HTTPException(400,'Invalid tool name')
        args=body.params.get('arguments',{})
        if not isinstance(args,dict) or set(args)-{'clinic_id','query'} or not isinstance(args.get('clinic_id'),str) or not isinstance(args.get('query',''),str): raise HTTPException(400,'Invalid tool arguments')
        data=call_tool(user,body.params.get('name'),args['clinic_id'],args.get('query',''))
        import json
        result={'content':[{'type':'text','text':json.dumps(data)}],'isError':False}
    else: raise HTTPException(400,'Unsupported MCP method')
    return {'jsonrpc':'2.0','id':body.id,'result':result}

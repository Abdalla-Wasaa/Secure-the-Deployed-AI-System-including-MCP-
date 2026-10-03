"""Authenticated MCP JSON-RPC tools/list and tools/call, HTTP transport."""
import json
from pathlib import Path
from fastapi import HTTPException
from injection_guard import guard
from rbac import allowed
APPROVED = frozenset(json.loads((Path(__file__).parent/'clinics_allowlist.json').read_text())['clinics'])
TOOLS = {'check_stock','plan_delivery_route'}
def call_tool(principal, name, clinic_id, query=''):
    guard(query)
    if name not in TOOLS or not allowed(principal['role'], name):
        raise HTTPException(403, 'Tool denied')
    if clinic_id not in APPROVED or clinic_id not in principal['clinics']:
        raise HTTPException(403, 'Clinic denied')
    # Deterministic lab stub: no environment enumeration or clinic listing.
    if name == 'check_stock': return {'clinic_id':clinic_id, 'available':True, 'source':'lab_fixture'}
    return {'clinic_id':clinic_id, 'delivery_window':'09:00-12:00', 'source':'lab_fixture'}

# Overview
Standalone Week 9 defensive capstone for AfyaPlus. FastAPI JWT boundaries, clinic-scoped MCP JSON-RPC lab tools, privacy-safe audit records, Kenya DPA teaching artefacts and a [manager brief](manager_brief.md). No live patient data or real clinical decisions.

Run from this directory with Python 3.12:
```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
python check_gitignore.py
python scripts/evidence.py
# Inject JWT_SECRET and SUBJECT_PEPPER securely (each at least 32 bytes).
APP_ENV=lab uvicorn app:app --host 127.0.0.1
```
Tests inject disposable generated secrets; no reusable JWT or credentials are shipped. JWTs require HS256, issuer afyaplus-auth, audience afyaplus, expiry, issued-at, subject, role and a list of clinics. Tokens are issued by a trusted external authority, not this service. POST /triage accepts message and clinic_id. POST /mcp accepts authenticated JSON-RPC initialize, tools/list and tools/call; it is a constrained HTTP lab implementation, not a full production MCP transport. Example tools/call params: {"name":"check_stock","arguments":{"clinic_id":"KSM-01"}}.

# Encryption
[transit_policy.py](transit_policy.py) denies production HTTP; --lab permits HTTP only for loopback. It validates policy, not network certificates. Examples:
```sh
python transit_policy.py https://api.afyaplus.ke
python transit_policy.py http://api.afyaplus.ke # exits 1
python transit_policy.py --lab http://localhost:8000
python resolve_secrets.py # exits 1 without injected secrets
```
[resolve_secrets.py](resolve_secrets.py) resolves [secret_refs.yaml](secret_refs.yaml) without printing values. [kms_twin.json](kms_twin.json) maps Azure Key Vault and AWS Secrets Manager/KMS equivalents. No storage encryption implementation is claimed; production requires encrypted volumes and verified TLS ingress. [check_gitignore.py](check_gitignore.py) checks ignored and tracked paths; code review must also inspect content for accidentally embedded credentials.

# Access Control
[rbac.py](rbac.py) grants partner triage/stock, operations stock/routes and admin stock/routes/rights workflow authority. Unknown roles have no permissions. All clinic tools require both [clinic allowlist](clinics_allowlist.json) and signed token clinic scope. [injection_guard.py](injection_guard.py) blocks known override phrases before model and MCP calls with 400. Missing/invalid JWT returns 401; denied role/clinic/tool returns 403. Pattern screening has false positives and evasion limits; tool permissions remain independently enforced.

# Logging
Runtime audit path: runtime/audit_log.jsonl; [audit_log.jsonl](audit_log.jsonl) is synthetic sample evidence. [redact_then_hash.py](redact_then_hash.py) redacts common phones, IDs, emails and bearer/JWT shapes before SHA-256. Audit entries retain only hashes for actor/resource, controlled actions/outcomes, generated trace digest and time. Clinical payloads and token headers are omitted. Hashes are pseudonyms, not guaranteed anonymisation. Restrict runtime filesystem access; immutable remote storage is a future deployment control.

# Kenya DPA
[Legal review notes and ODPC sources](docs/legal_review.md).
[data_inventory.json](data_inventory.json), [retention.json](retention.json), [lawful_basis.json](lawful_basis.json) are teaching proposals. Legal review pending. Rights owner: designated privacy lead, appointment pending. [rights_lookup.py](rights_lookup.py) provides access and verified erasure on a local JSON store, using separate keyed subject hashes. Access is an operator function requiring identity verification before disclosure. [retention_sweep.py](retention_sweep.py) preserves [deletion_records.jsonl](deletion_records.jsonl), recording intent and completion. Invoke access/erase/sweep from an authorised operator workflow; no public rights endpoint. Retention is an explicit operator job, not automatically scheduled. Concurrent writers and distributed deletion require production storage transactions. Backups and downstream copies must be included in live rights procedures.

# Manager Brief
[manager_brief.md](manager_brief.md) includes Risks, Mitigations, Kenya DPA Alignment, What We Will Not Claim. The prohibited absolute-security word does not appear in the brief; tests verify headings and actual file references.

# Fallbacks
Local process secret injection is the lab fallback when Azure or AWS is unavailable; production fails closed rather than embedding keys. MCP stock/routes and model recommendations use deterministic local stubs, clearly labelled. Legal review pending; no approval or compliance certification is implied.

# Week Reuse
Read-only reference: ../venv/wk9/monday transit/injection/allowlist patterns, tuesday RBAC and redact-then-hash, thursday inventory/retention/rights/brief. Reimplemented independently: strict URL schemes, actual HTTP JWT enforcement, separate subject pepper, guarded model/tool boundaries, all-field audit minimisation, erasure and ledger-safe retention. No wk9 files modified or moved.

# Workflow and evidence
See [CONTRIBUTING.md](CONTRIBUTING.md), [docs/evidence.txt](docs/evidence.txt), and [docs/pull_request.md](docs/pull_request.md). CI runs tests and policy evidence. Cloud rollout, remote PR creation, branch protections and actual ingress checks remain deployment tasks requiring GitHub/cloud connectivity. Do not merge this feature branch until its remote PR is reviewed.

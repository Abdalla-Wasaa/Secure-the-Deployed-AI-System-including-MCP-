# AfyaPlus manager security brief

## Risks
Patient information could be exposed through excessive access, unsafe requests, leaked credentials or long storage periods. Simple request screening can miss new wording. Cloud protections and a real clinical model have not been deployed.

## Mitigations
- Encrypted partner connections are required by [transit_policy.py](transit_policy.py); actual hosting certificates still need verification.
- Startup stops without required secrets in [resolve_secrets.py](resolve_secrets.py); [check_gitignore.py](check_gitignore.py) checks excluded files.
- Staff permissions and approved clinic access are limited by [rbac.py](rbac.py), [clinics_allowlist.json](clinics_allowlist.json), [app.py](app.py) and [mcp_server.py](mcp_server.py).
- Known attempts to override instructions are rejected by [injection_guard.py](injection_guard.py) before recommendations or tool use. Screening is imperfect.
- [redact_then_hash.py](redact_then_hash.py) removes common identifying patterns and records limited audit information.
- [retention_sweep.py](retention_sweep.py) removes expired records and preserves deletion evidence; [rights_lookup.py](rights_lookup.py) supports verified requests.

## Kenya DPA Alignment
[data_inventory.json](data_inventory.json) describes information use. [retention.json](retention.json) proposes storage periods. [lawful_basis.json](lawful_basis.json) records unresolved legal questions. Legal review pending. Management must appoint a privacy lead, approve notices, assess sensitive health information and cross-border transfers, and establish incident response before live use.

## What We Will Not Claim
We do not claim guaranteed compliance, legal certification, complete protection or deployed cloud encryption. These are tested teaching controls with remaining operational and legal work.

The system recommends rather than decides and must remain under human oversight.

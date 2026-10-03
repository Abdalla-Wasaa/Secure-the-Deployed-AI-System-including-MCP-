## Summary
Publish the standalone AfyaPlus Week 9 security capstone with semantic commit history and the v1.0.0 release.

## Week 9 deliverables
- Encryption policy: production HTTPS enforcement, loopback-only lab fallback, fail-closed injected secrets, Azure/AWS vault and KMS mapping, and credential exclusions.
- Access control: JWT-protected FastAPI triage, role permissions, signed clinic scope and allowlist enforcement, constrained MCP tools, and prompt-injection screening.
- Logging: redaction before hashing, minimal pseudonymous audit events, synthetic evidence, and separate runtime logs.
- Privacy workflows: data inventory, proposed lawful basis and retention, verified subject access/erasure, and ledger-safe retention sweeps.
- Management submission: Kenya DPA review notes, risks and mitigations, manager brief, operational limitations, and local stub fallbacks.
- Engineering: pinned dependencies, contributor workflow, automated CI, 28 security tests, and policy evidence generation.

## Validation
- pytest -q: 28 passed.
- check_gitignore.py: 8 probes passed; no forbidden tracked paths.
- Full commit-history scan: no forbidden paths or common credential signatures found; secret mappings contain environment references only.

## Release and limitations
Merge with a merge commit to preserve semantic history, then publish annotated tag v1.0.0. This is a teaching implementation with synthetic data and local MCP/model stubs. Production TLS, encrypted storage, transactional persistence, designated privacy ownership and legal review remain required.

# Open Source Hardening Task List

Use this checklist to create GitHub issues and track release readiness work.

## P0 - Stabilization

- [ ] CI: verify installation path using `pip install -e '.[dev]' --no-build-isolation`.
- [ ] CI: require `PYTHONPATH=src python scripts/validate_all.py` on every pull request.
- [ ] Docs: keep troubleshooting section synced with real failures and fixes.
- [ ] Docs: verify mirror-based installation instructions in constrained networks.

## P1 - Security

- [ ] CI: enforce `pip-audit --strict` on pull requests.
- [ ] CI: enforce secret scanning for full repository history in pull requests.
- [ ] Policy: define dependency update cadence and ownership.
- [ ] Release: publish artifact checksums and signed tags.

## P1 - Determinism and Contracts

- [ ] Add regression fixtures for deterministic JSON output ordering.
- [ ] Add tests for numeric consistency and policy boundary conditions.
- [ ] Add schema compatibility check for changed contracts/schemas.
- [ ] Add Python vs Rust parity test cases for shared snapshots.

## P2 - OSS Operations

- [ ] Add roadmap issue with explicit non-goals.
- [ ] Add `good first issue` backlog for external contributors.
- [ ] Define triage SLA for bug and security issues.
- [ ] Add maintainer release checklist issue template.

## Recommended Labels

- `priority:p0`
- `priority:p1`
- `priority:p2`
- `area:ci`
- `area:security`
- `area:docs`
- `area:validation`
- `area:release`

## Suggested Milestones

- `v0.1.x Stabilization`
- `v0.2.x Hardening`
- `v0.3.x OSS Operations`

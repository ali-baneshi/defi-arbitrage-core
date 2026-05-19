# Open Source Release Plan

This plan focuses on making the repository reliable, auditable, and contributor-friendly before broad public adoption.

## Goals

- Keep the project boundary strict: offline deterministic analysis only.
- Ensure installs, validation, and release checks are reproducible in constrained networks.
- Reduce operational and security risk for maintainers and users.
- Publish a clear contribution and support model.

## Phase 0: Immediate Stabilization (P0)

- Installation hardening
  - Keep `make bootstrap` as the canonical local setup.
  - Support mirror-based package indexes for restricted environments.
  - Add CI check that verifies setup commands in a clean virtualenv.
- Build reliability
  - Make `scripts/validate_all.py` the minimum release gate.
  - Fail CI if schema-validation scripts fail.
- Documentation quality
  - Keep README quick-start path to 3-5 commands max.
  - Ensure troubleshooting covers shell quoting, venv, and mirror usage.

Exit criteria:
- A new maintainer can run validation from a fresh machine without manual patching.
- Baseline checks pass in local + CI using documented commands.

## Phase 1: Security and Hardening (P1)

- Supply-chain and dependency controls
  - Pin dev tooling versions in CI jobs.
  - Add dependency vulnerability scan in CI.
  - Add secret scanning for commits and pull requests.
- Runtime safeguards
  - Add explicit limits for snapshot size and edge counts (DoS protection).
  - Improve error taxonomy for malformed input vs internal failures.
- Release integrity
  - Generate signed release artifacts.
  - Publish checksums and release evidence.

Exit criteria:
- CI enforces secret/dependency checks on pull requests.
- Releases include verifiable artifact integrity metadata.

## Phase 2: Determinism and Compatibility (P1)

- Deterministic behavior
  - Add golden tests for JSON output ordering and numeric formatting.
  - Validate consistent behavior across Python supported versions.
- Compatibility policy
  - Publish schema compatibility guarantees (backward/forward expectations).
  - Add migration notes per breaking change.
- Optional Rust parity
  - Add parity tests comparing Python and Rust-backed output on shared fixtures.

Exit criteria:
- Deterministic output regression suite is mandatory in CI.
- Schema compatibility checks are automated and enforced.

## Phase 3: Open Source Operations (P2)

- Contribution workflow
  - Add issue templates (bug, feature, docs, security concern).
  - Add PR template with release-impact and risk checklist.
- Maintainer operations
  - Define triage SLAs and support boundaries in docs.
  - Maintain changelog discipline with semantic release notes.
- Community readiness
  - Label first issues for external contributors.
  - Document roadmap and non-goals to avoid scope drift.

Exit criteria:
- External contributors can submit useful PRs without private context.
- Repo governance and release expectations are explicit.

## Risk Register (Top Priority)

- Installation drift across shells and package managers.
- Network constraints causing broken onboarding.
- Silent schema drift between docs, scripts, and runtime.
- Scope creep toward execution-bot features.
- Incomplete security posture before wider adoption.

## Suggested Owners

- Core maintainer: architecture, boundary, release approval.
- CI owner: pipeline gates, deterministic checks, scanners.
- Docs owner: README, troubleshooting, contributor onboarding.
- Security owner: policy, disclosure handling, dependency and secret hygiene.

## 30/60/90-Day Delivery Outline

- 30 days
  - Complete Phase 0 and baseline CI hardening.
- 60 days
  - Complete Phase 1 and begin deterministic output suite.
- 90 days
  - Complete Phase 2 and foundational Phase 3 governance.

## Definition of Done for Public Promotion

- Installation and validation are reproducible in documented constrained-network scenarios.
- Security and dependency checks are mandatory and passing.
- Deterministic output and schema compatibility checks are mandatory and passing.
- README and docs are consistent with actual behavior.
- Release process has verifiable evidence and rollback guidance.

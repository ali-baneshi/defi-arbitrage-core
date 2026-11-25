# Decision log

This file is the audit trail for the reduction. Each entry states the decision,
evidence, rejected alternatives, and how to reverse it.

## 2026-11-25 — D1: primary user is a local researcher

**Decision.** The CLI is the product. The library remains a small embeddable
API but is not a second product with its own support surface.

**Evidence.** The only reachable workflow is a local file plus a local report.
No ingestion, service, or persistence layer exists.

**Rejected.** A backend-embedding product would require stable versioned APIs,
more extension points, and a service contract that the repository does not
have. A reviewer-only artifact would not justify tests or bounds.

**Reversal.** Add an explicit embedding guide and API-stability policy; no code
deletion is required.

## 2026-11-25 — D2: English is the only maintained documentation language

**Decision.** Delete `docs/fa/`, `docs/zh/`, `docs/TRANSLATION_STATUS.md`, and
the localization release gate. `docs/en/` and the root README are canonical.

**Evidence.** 79 Markdown files under `docs/`, 3,702 lines, with duplicated
status/release narratives. The localization gate is a manual attestation that
cannot be checked by code, and no localization owner or parity test exists.

**Rejected.** Keeping locales behind a parity gate would require a runnable
translation-parity check and a maintenance commitment that the project does not
have.

**Reversal.** Restore the locale trees from git history and add a parity test
before accepting translations again.

## 2026-11-25 — D3: remove the Rust analyzer

**Decision.** Delete `rust/`, `arbcore/service.py`, Rust parity fixtures,
Rust-specific scripts/tests, CI steps, and Docker copies.

**Evidence.** The crate is 627 lines plus tests and parity fixtures, mirrors a
129-line Python engine, and has no named production user or committed
benchmark. Parity is maintained by hand and can drift. The Python engine with
a budget is adequate for the stated job.

**Rejected.** Keeping Rust "for speed" without a measured workflow. A real
acceleration case would need a profile on realistic snapshots, a parity gate
in CI, and a documented fallback contract.

**Reversal.** Restore the crate and adapter from git history, then add a
committed benchmark proving the speedup and a parity test on every supported
fixture.

## 2026-11-25 — D4: remove the smart-contract templates

**Decision.** Delete `contracts/`, `arbcore/contracts/`, contract schemas,
validator, scripts, tests, and docs.

**Evidence.** 54 lines of inert Solidity/Vyper source plus a manifest and 573
lines of Python validation. Nothing is compiled, deployed, or consumed by the
analysis engine. The templates cannot execute and are not an audit.

**Rejected.** Keeping templates as "examples" would preserve a second product
with a different threat model and no test that proves safety.

**Reversal.** Restore the subtree from history if a separate, audited
integration product is created; do not reattach it to this analyzer.

## 2026-11-25 — D5: replace the release-evidence gate with a checklist

**Decision.** Delete `release/`, the evidence schema/validator, the readiness
script and golden fixture, and their CI steps. Add a short maintainer release
checklist in `docs/en/RELEASE_CHECKLIST.md`.

**Evidence.** The gate reports `public_release_ready: false` on a clean
checkout because `release/release-evidence.json` is not shipped; the script
still exits 0, so CI cannot enforce it. The evidence requirements are manual
attestations unrelated to whether the analyzer works.

**Rejected.** Shipping a satisfied evidence file would be an unverifiable
claim. Keeping the blocked gate preserves process theater.

**Reversal.** Restore the scripts and schema from history; make the gate exit
non-zero when blocked and require evidence that can actually be produced.

## 2026-11-25 — D6: remove the path allow-list

**Decision.** Accept any normal filesystem path. Delete `path_utils.py`, the
CWD/temp restriction, the symlink checks, and the `--rust-binary` path policy.
Keep file-size, UTF-8, JSON, and schema checks.

**Evidence.** The tool's input is a file the user explicitly names. The
sandbox rejects legitimate absolute paths and has no stated threat model. Its
symlink logic is incomplete.

**Rejected.** Keeping the sandbox with better messages would still break
normal CLI use without protecting a secret.

**Reversal.** Reintroduce an explicit opt-in `--allow-root` policy if this ever
runs as a service over untrusted paths. Do not make it the default.

## 2026-11-25 — D7: one package identity and one console script

**Decision.** Keep the distribution name `defi-arbitrage-core`, the import
package `arbcore`, and the console script `defi-arbitrage-core`. Delete the
`defi_arbitrage_core` shim and the `arbcore` console script. Add
`python -m arbcore`.

**Evidence.** The shim contains no behavior. Two import names and two scripts
create ambiguity in installs, docs, and tests.

**Rejected.** Keeping the shim indefinitely would require compatibility policy
and duplicate test coverage.

**Reversal.** Restore the shim as a deprecated compatibility package in a
minor release if real users depend on it. Existing imports in this repository
do not.

## 2026-11-25 — D8: remove edge metadata

**Decision.** Remove `metadata` from `Edge`, input validation, schemas, tests,
and fixtures.

**Evidence.** No code reads metadata. It costs depth/size checks, 1 MiB and
10 MiB limits, test surface, and schema drift.

**Rejected.** Keeping metadata "for future integrations" is speculative and
can be added with a concrete consumer.

**Reversal.** Add a versioned input field with a real consumer, schema update,
and bounds test.

## 2026-11-25 — D9: enforce a search-expansion budget

**Decision.** Keep `max_hops <= 8` and degree `<= 500`, but add a deterministic
2,000,000 edge-expansion budget that aborts with `AnalysisLimitError`, and keep
at most four times `max_results` candidates during the search.

**Evidence.** 12 assets / 132 edges: 5 hops = 1.19M expansions (1.27 s),
6 hops = 8.51M expansions (9.60 s), 7 hops = 52.4M (72 s). The 2M budget
admits 12 assets at 5 hops and aborts 6 hops in about two seconds. `max_results`
does not limit work, and an unbounded candidate map would otherwise grow with
the number of profitable cycles.

**Rejected.** Lowering `max_hops` to 6 would still take 9 s on 12 assets and
would arbitrarily exclude legitimate sparse graphs. A worst-case formula from
degree counts is too pessimistic for sparse graphs.

**Reversal.** Tune `MAX_SEARCH_EXPANSIONS` with a new committed benchmark; the
error path and tests stay.

## 2026-11-25 — D10: remove environment configuration and default snapshot

**Decision.** Delete `config.py`, all `ARBCORE_*` variables, and the implicit
default snapshot. `SNAPSHOT` is a required argument; policy flags have
documented defaults.

**Evidence.** Env settings duplicate CLI flags, and `Settings.from_env()` can
fail before `--show-policy` even when no snapshot is needed. The default
snapshot only exists in a checkout.

**Rejected.** Keeping env vars for containers is speculative; containers can
pass arguments.

**Reversal.** Add explicit flags first, then an env layer only with a
documented precedence test.

## 2026-11-25 — D11: clarify the economic contract, do not expand it

**Decision.** Keep the linear model. Rename documentation to "nominal
candidate", state that fees are percentage deductions, that liquidity is a
quote bound, and that gas/slippage/MEV/decimals are not modeled.

**Evidence.** The engine is a cycle enumerator over scalar quotes. Modeling
execution would require external data and a different product.

**Rejected.** Adding a slippage curve or gas estimate without data would make
the output look more precise without making it more accurate.

**Reversal.** Only with a data contract and validation for the new inputs.

## 2026-11-25 — D12: keep the MIT license and distribution name

**Decision.** No license change and no distribution rename in this work.

**Evidence.** Renaming or relicensing would break existing users and require
owner approval. The reduction does not require either.

**Rejected.** A rename to `arbcore` would be cosmetic and disruptive.

**Reversal.** Requires explicit owner and legal review; out of scope here.

## 2026-11-25 — D13: use the narrow production-ready definition

**Decision.** Treat `docs/en/PRODUCT.md` as the production-ready bar. The
result may be called production-ready for offline nominal analysis only; it is
not trading-ready.

**Evidence.** `docs/en/FINAL_AUDIT.md` records the eight checks and the
remaining model limitations.

**Rejected.** Calling the project production-ready without qualification would
overstate a linear model with no execution, gas, slippage, or settlement.

**Reversal.** Remove the verdict or tighten the definition; do not widen the
model without a new input contract and tests.

## Open question defaults

The six Phase 0 questions were answered by default because the mandate says to
keep moving: local researcher; live execution permanently out of scope;
localization not a commitment; Rust an experiment; release gate replaced by a
checklist; the listed surfaces removable. Any of these can be reversed using
the entries above.

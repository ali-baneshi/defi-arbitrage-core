# Changelog

All notable changes to `defi-arbitrage-core` should be documented in this file.

## Unreleased

### Added
- Explicit multi-network snapshot and opportunity support through the `network` field
- Public `defi_arbitrage_core` Python package alias and `defi-arbitrage-core` CLI entrypoint
- Additional example snapshot for Base
- Stronger Rust/Python parity checks and fail-closed response validation
- Multilingual documentation refresh for English, Persian, and Chinese core pages

### Changed
- Public project branding from Polygon-specific naming to `defi-arbitrage-core`
- README positioning toward deterministic DeFi analysis infrastructure instead of bot framing
- Output/reporting now preserves network identity

### Fixed
- Contract validation path resolution from manifest location
- UTF-8 decoding failures now surface as safe project-specific errors
- Rust adapter now rejects malformed top-level payloads and malformed numeric fields safely

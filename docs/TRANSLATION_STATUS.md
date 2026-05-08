# Translation Status

English documentation in `docs/en/` is canonical for release, validation, security, runbook, and smart-contract behavior.

| Locale | Status | Release-Critical? | Notes |
| --- | --- | --- | --- |
| English (`docs/en`) | canonical-current | yes | Source of truth for public release decisions. |
| Persian (`docs/fa`) | localized-current | no | Mirrored public documentation set refreshed against the current English docs; English remains canonical for release details. |
| Chinese (`docs/zh`) | localized-current | no | Mirrored public documentation set refreshed against the current English docs; English remains canonical for release details. |

## Translation Process

1. Update `docs/en/` first.
2. Refresh the matching Persian and Chinese pages in the same change when practical.
3. If localized docs cannot be fully updated, keep English canonical and record the gap here.
4. Do not claim multilingual release parity unless this table is updated deliberately.

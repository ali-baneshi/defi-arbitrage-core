# Release Evidence

Copy `release-evidence.example.json` to `release-evidence.json` in a private
working tree while preparing the release, or keep the completed non-secret
attestation elsewhere and pass it with `--evidence-file`. Commit it only after
independent scans, credential rotation, history cleanup, and localization review
are complete.

The readiness script reads `release/release-evidence.json` by default. A missing
file or any blocked/failed gate keeps public release readiness false.

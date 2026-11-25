# Changelog

## 1.10.0

### Added
- **Security posture module** (`modules/security.py`): 22 read-only checks across 7 categories, severity-weighted score, coverage reporting, stable finding IDs and fingerprints, per-scan case ID.
- **Opt-in reversible fixes** (`modules/security_fix.py`): dry-run by default, journal of applied changes, rollback.
- `modules/registry_io.py` (winreg layer), `modules/version.py` (single version source).
- Test suite: 38 unit tests (`python -m unittest discover -s tests -t . -v`).
- Security results included in the JSON report and shown in the scan log.

### Changed
- **TEMP cleanup now only removes items untouched for 24 hours or more**; folders containing recent writes are kept.
- **The Recycle Bin is no longer emptied automatically** (irreversible data loss).
- `run_powershell` no longer passes `-ExecutionPolicy Bypass` (not needed with `-Command`; commonly flagged by EDR).
- `run_silent` decodes output with `errors="replace"` and accepts an explicit `encoding` (no crashes on non-English output).
- Per-user data directory helper (`get_data_dir`) for locations that must stay writable when installed under Program Files.
- Version string unified (previously 1.9.1 / 1.9.0 / 1.6.2 / 1.4 across files).

### Fixed
- **PowerShell output arriving with a UTF-8 BOM made every PowerShell-backed security check (and signature lookup) silently fail** — found on the first real Windows run. Output parsing now tolerates a BOM and stray lines; regression-tested.
- PowerShell data collection is split into three independent parts that run in parallel, so one slow or failing cmdlet (e.g. `Get-HotFix` on an old machine) no longer takes the others down; each `UNKNOWN` now says why.
- Startup-program check no longer reports "trusted" when the signature lookup was unavailable (now `UNKNOWN`).
- A scan with under 70% check coverage is marked provisional with no letter grade, instead of showing a misleading "B".
- Removed hardcoded `D:` / `E:` drive letters from the fix plan; advice now names the actual drive.

## 1.9.1
- CustomTkinter dashboard: layered surfaces, KPI accents, host strip, finding chips.

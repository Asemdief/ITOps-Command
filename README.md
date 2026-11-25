<div align="center">

# ITOps Command

**Windows endpoint diagnostics and security posture audit.**
Silent. Local. Honest about what it can't see.

![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-1c1c1f?style=flat-square&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/python-3.10%2B-1c1c1f?style=flat-square&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/status-beta-22d3ee?style=flat-square)
![Version](https://img.shields.io/badge/version-1.10.0-1c1c1f?style=flat-square)
![License](https://img.shields.io/badge/license-proprietary-71717a?style=flat-square)

</div>

---

ITOps Command turns raw Windows telemetry into **root-cause findings, a prioritised fix plan, and a security posture score with evidence** — in one double-click windowed app, with no black console flashing on screen and nothing leaving the machine.

```
Instead of    RAM 87%  ·  Disk C: 91%  ·  ping failed
You get       High memory pressure · Critical free space on C:
              Top consumers · prioritised fix plan
              Internet OK (DNS/TCP path verified — not ICMP-only)

              Security 17/100 (F) · 20 of 22 checks evaluated
              FAIL  Antivirus real-time protection off   [CRITICAL]
              FAIL  RDP enabled without NLA              [HIGH]
              FAIL  SMBv1 enabled                        [HIGH]
```

> **Status — Beta (v1.10.0).** The diagnostics pipeline is in daily use. The new security module is covered by automated tests that use mocked registry/PowerShell data; validation on real hardware (Windows 10/11, admin and standard, non-English locale) is in progress. See [Known limitations](#known-limitations).

## Who it's for

Helpdesk L1–L2, sysadmins, MSP technicians and small IT teams who need a fast, consistent look at a machine — and consultants who need pre-audit evidence of its security posture.

## What it does

### Diagnostics

| Area | What you get |
|---|---|
| **Inventory** | Host, user, OS, CPU, RAM, disk partitions and status |
| **Network** | Active adapter (virtual adapters filtered), gateway, DNS, internet path, latency |
| **Processes** | Top CPU / RAM consumers with system noise filtered |
| **Health** | Score 0–100 from CPU, RAM and disk pressure |
| **Root cause** | Plain-language issues with a prioritised fix plan |
| **History** | Delta versus the previous run |
| **Reports** | HTML + JSON written locally, next to the app |

### Security posture — 22 read-only checks

| Category | Checks |
|---|---|
| **Endpoint Protection** (4) | Real-time protection · signature freshness · tamper protection · Defender exclusions |
| **Network & Exposure** (5) | Firewall (all profiles) · Remote Desktop / NLA · SMBv1 · LLMNR · risky listening ports |
| **Disk & Boot** (2) | BitLocker on the system drive · Secure Boot |
| **Accounts & Access** (5) | UAC · local administrators count · Guest account · built-in Administrator · inactivity lock |
| **Credential Protection** (2) | WDigest plaintext caching · LSA protection (RunAsPPL) |
| **Patching** (2) | Age of last installed update · pending reboot |
| **Persistence & Logging** (2) | Startup programs (signature + location) · PowerShell script block logging |

Every finding carries a **stable ID** (`ITC-001`…), **severity**, **expected vs. actual**, **evidence**, **remediation steps**, and a short **fingerprint** so the same state can be tracked across scans. Each scan gets a **case ID**.

**How the score works**

- Severity-weighted: `CRITICAL 10 · HIGH 6 · MEDIUM 3 · LOW 1`; a warning earns half credit.
- Any failed `CRITICAL` check **caps the score at 59** — a machine with plaintext credential caching can't grade "B".
- A check that can't be evaluated (needs admin, tool unavailable) is marked `UNKNOWN` / `NEEDS_ADMIN`, **excluded from the score, and reported as lower coverage** (e.g. *20 of 22 evaluated*). It is never guessed and never penalised.
- **Low coverage means no letter grade.** If fewer than 70% of the checks could be evaluated, the score is shown as *provisional* with grade `N/A` — a "B" built on half the checks would be misleading. Every `UNKNOWN` states why (e.g. *PowerShell part timed out*).

> Check areas are inspired by common hardening baselines, but the IDs and labels are ITOps Command's own — this is not an official CIS benchmark implementation.

### Reversible fixes (opt-in)

`modules/security_fix.py` can remediate selected findings (RDP NLA, SMBv1, LLMNR, UAC, inactivity lock, WDigest, LSA protection, PowerShell logging):

- **Dry-run by default** — shows exactly what would change, the previous value, the impact and whether a reboot is needed.
- **Journaled** — every applied change is recorded with its previous value.
- **Rollback** — any journaled change can be undone.
- Registry DWORD changes only. Nothing irreversible belongs here.

> The fix API is complete and tested; the UI for it is on the roadmap.

### Automatic housekeeping during a diagnostic

Deliberately small and conservative: flushes the DNS cache, and removes TEMP items that have not been modified for **24 hours or more** (anything recently touched — including folders with a recently written file inside — is left alone). **The Recycle Bin is never emptied automatically.**

## Design principles

1. **The security scan never changes the machine.** Read-only, always.
2. **No console flash.** Every system command goes through `modules/win_silent.py` (`CREATE_NO_WINDOW`, never `shell=True`).
3. **Locale-independent where it matters.** Registry reads, PowerShell returning JSON objects, and well-known SIDs instead of localised account names.
4. **Honest coverage.** What can't be checked is reported as unchecked.
5. **Network truth.** DNS resolution **or** TCP/HTTPS success means *Internet OK*. An ICMP ping failure alone never marks a machine offline.
6. **Local-first.** No telemetry, no uploads, no account. Reports stay on the machine. Connectivity checks contact public endpoints (Microsoft connect-test, Cloudflare / Google / Quad9 DNS) only to test reachability.

## Sample output

*Generated from mocked data to show the format — not a real machine.*

```
CASE ITC-20261115-1200-2472   elevated=False
SCORE 17/100 (F)   coverage 20/22   [capped by CRITICAL failure]

[FAIL       ] CRITICAL ITC-001  Antivirus real-time protection   ->  Disabled
[FAIL       ] HIGH     ITC-010  Windows Firewall (all profiles)  ->  Off: Public
[FAIL       ] HIGH     ITC-011  Remote Desktop exposure          ->  Enabled WITHOUT NLA
[FAIL       ] HIGH     ITC-012  SMBv1 server protocol            ->  Enabled
[NEEDS_ADMIN] MEDIUM   ITC-004  Defender exclusions              ->  Requires administrator
[WARN       ] MEDIUM   ITC-041  LSA protection (RunAsPPL)        ->  Not enabled
[PASS       ] MEDIUM   ITC-032  Guest account disabled           ->  Disabled
```

## Quick start

**Requirements:** Windows 10 / 11, Python 3.10+ (source runs), `psutil`, `customtkinter`.

```bat
git clone https://github.com/Asemdief/ITOps-Command.git
cd ITOps-Command
pip install -r requirements.txt
run_gui.vbs
```

`run_gui.vbs` / `run_gui.bat` start the app **without a console window**. (Plain `python gui.py` always shows one — `python.exe` is a console program. Use `pythonw gui.py` if you prefer the command line.)

Run as **Administrator** for full security coverage; without elevation some checks report `NEEDS_ADMIN`.

Developer commands:

```bat
python -m modules.security                      :: security scan to the console (dev only)
python -m unittest discover -s tests -t . -v    :: run the test suite
```

### Build a standalone `.exe`

```bat
build_exe.bat
```

Produces `dist\ITOps-Assistant.exe` (`--onefile --windowed --noconsole`). Unsigned executables may trigger SmartScreen or antivirus warnings; code signing is planned.

## Project layout

```
ITOps-Command/
├── gui.py                  # CustomTkinter UI + scan orchestration (background thread)
├── modules/
│   ├── inventory.py        # System / CPU / RAM / disks
│   ├── network.py          # Adapter, gateway, DNS, internet probes
│   ├── processes.py        # Top CPU / RAM consumers
│   ├── health.py           # Health score 0–100
│   ├── root_cause.py       # Issues from telemetry
│   ├── fix_plan.py         # Prioritised suggestions
│   ├── fix_engine.py       # Conservative silent housekeeping
│   ├── security.py         # 22-check posture scan + scoring (read-only)
│   ├── security_fix.py     # Opt-in fixes: dry-run, journal, rollback
│   ├── registry_io.py      # winreg access layer
│   ├── history.py          # Previous run + deltas
│   ├── export.py           # HTML + JSON reports
│   ├── win_silent.py       # Hidden-window process helpers
│   ├── paths.py            # App dir (source + frozen) and per-user data dir
│   └── version.py          # Single source of truth for the version
├── tests/                  # 38 unit tests (unittest)
├── docs/SECURITY_MODULE.md # Security module design notes
├── build_exe.bat · run_gui.bat · run_gui.vbs
├── version_info.txt · icon.ico · requirements.txt
├── CHANGELOG.md · LICENSE
└── README.md
```

## Known limitations

Being upfront, because this is a security tool:

- **Security module — real-hardware validation is ongoing.** Logic is unit-tested with mocks, and a first run on Windows 10 has already surfaced and fixed a PowerShell output-encoding bug. BitLocker detection and registry semantics across Windows builds still need confirmation on more machines. If something looks wrong, `python -m modules.security --debug` prints the raw collector diagnostics.
- **Network layer assumes English output** from `ipconfig` / `ping`. On non-English Windows the gateway or latency may show `n/a`. A locale-independent rewrite is planned.
- **Gateway check uses ICMP**, so a router that blocks ping can show a false "gateway issue" even when internet works.
- **Captive portals** can answer the HTTP probe and be reported as *Internet OK*.
- **Health score ≠ security score.** The health score reflects CPU / RAM / disk pressure only; security posture is scored separately.
- **History** keeps only the previous snapshot.
- **Unsigned builds** may be flagged by SmartScreen / AV.

## Roadmap

| Next | Focus |
|---|---|
| Real-hardware validation | Windows 10 / 11, admin and standard, English and Arabic locale |
| New interface | Live scan sequence, security tab, per-finding evidence view, fix preview and rollback |
| Locale-independent network layer | Native APIs instead of parsing localised command output |
| Reporting | PDF export, white-label reports, trend history (SQLite) |
| Distribution | Installer, code signing, update channel |
| Exploratory | Multi-device / MSP management |

## License

Proprietary — **all rights reserved**. The source is visible for evaluation only; see [`LICENSE`](LICENSE). For commercial licensing or custom builds, contact the maintainer through GitHub.

## Maintainer

**Asem Dief** — [github.com/Asemdief](https://github.com/Asemdief)

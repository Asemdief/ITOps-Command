 <div align="center">

# ⚡ ITOps Command

### Windows Endpoint Intelligence & Security Assessment

**Diagnose. Understand. Secure.**

A local-first Windows IT Operations tool that transforms endpoint telemetry into actionable diagnostics, root-cause insights, and security posture assessments.

![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-0078D4?style=for-the-badge&logo=windows)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python)
![Version](https://img.shields.io/badge/Version-1.10.0-0F766E?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Beta-D97706?style=for-the-badge)
![License](https://img.shields.io/badge/License-Proprietary-52525B?style=for-the-badge)

</div>

---

## 🚀 Overview

ITOps Command is designed to simplify Windows endpoint troubleshooting and security assessment.

Instead of manually checking Task Manager, network configuration, system resources, and security settings, technicians can use one application to collect system information, identify operational issues, and review security weaknesses.

**Built for:**
- IT Helpdesk & Technical Support
- IT Operations Engineers
- System Administrators
- MSP Technicians
- Endpoint Security Assessment

## ✨ Core Capabilities

### 🖥️ Endpoint Diagnostics

| Module | Capability |
|---|---|
| System Inventory | Hostname, OS, CPU, RAM, disks |
| Network Diagnostics | Adapters, DNS, gateway, connectivity |
| Process Analysis | CPU and memory consumers |
| System Health | Resource-based health score |
| Root Cause Analysis | Identify and explain operational issues |
| Fix Planning | Prioritized troubleshooting recommendations |
| History | Compare previous diagnostic runs |
| Reporting | Local HTML and JSON reports |

### 🛡️ Security Posture Assessment

Evaluate Windows security configuration through **22 read-only checks across 7 security categories**.

| Category | Security Checks |
|---|---|
| Endpoint Protection | Defender status, signatures, tamper protection, exclusions |
| Network & Exposure | Firewall, RDP/NLA, SMBv1, LLMNR, listening ports |
| Disk & Boot | BitLocker, Secure Boot |
| Accounts & Access | UAC, administrators, Guest, inactivity lock |
| Credential Protection | WDigest, LSA Protection |
| Patching | Update age, pending reboot |
| Persistence & Logging | Startup programs, PowerShell logging |

Each finding includes:
- Stable Finding ID
- Severity classification
- Expected vs. actual configuration
- Supporting evidence
- Remediation guidance
- Finding fingerprint

### 📊 Security Scoring

The security score uses severity-weighted evaluation.

| Severity | Weight |
|---|---:|
| CRITICAL | 10 |
| HIGH | 6 |
| MEDIUM | 3 |
| LOW | 1 |

**Scoring principles:**
- Critical failures cap the score at 59.
- Warnings receive half credit.
- Unavailable checks are marked UNKNOWN or NEEDS_ADMIN.
- Unknown checks are excluded from scoring.
- Coverage below 70% produces a provisional result without a letter grade.

> This is an internal assessment model, not an official CIS Benchmark implementation or compliance certification.

### 🔧 Reversible Security Remediation

The security remediation API supports selected configuration changes.

- Dry-run by default.
- Previous values are journaled.
- Applied changes can be rolled back.
- Explicit execution is required.

**Note:** The remediation API exists, but its dedicated GUI workflow is still under development.

### ⚙️ Automated Housekeeping

Conservative maintenance actions:

- Flush DNS cache.
- Remove TEMP items untouched for at least 24 hours.
- Preserve recently modified files and folders.
- Never automatically empty the Recycle Bin.

---

## 🧠 Design Philosophy

ITOps Command follows six principles:

1. **Local-first:** Diagnostic reports remain on the endpoint.
2. **Read-only security assessment:** Scanning does not modify security settings.
3. **Evidence-based findings:** Results should explain why something was flagged.
4. **Honest coverage:** Unavailable information is never treated as a pass.
5. **Safe remediation:** Changes require explicit opt-in.
6. **Operational clarity:** Findings should help technicians decide what to investigate next.

Connectivity checks contact public endpoints to verify reachability; the application does not claim to operate without network traffic.

## 📸 Application Preview

<!-- Add real application screenshots here -->

| Dashboard | Security Assessment |
|---|---|
| Add dashboard screenshot | Add security results screenshot |

| Diagnostic Report | Root Cause Analysis |
|---|---|
| Add report screenshot | Add root-cause screenshot |

## 🚀 Installation

### Requirements

- Windows 10 / 11
- Python 3.10+
- Administrator privileges recommended

### Run from source

\`\`\`powershell
git clone https://github.com/Asemdief/ITOps-Command.git

cd ITOps-Command

python -m pip install -r requirements.txt

.\run_gui.vbs
\`\`\`

Alternative launch:

\`\`\`powershell
.\run_gui.bat
\`\`\`

### Build executable

\`\`\`powershell
.\build_exe.bat
\`\`\`

Output:

\`\`\`text
dist\ITOps-Assistant.exe
\`\`\`

The current executable is unsigned and may trigger Windows SmartScreen or antivirus warnings.

## 🧪 Testing

Run the automated test suite:

\`\`\`powershell
python -m unittest discover -s tests -t . -v
\`\`\`

Run security diagnostics:

\`\`\`powershell
python -m modules.security --debug
\`\`\`

Current automated test suite: **38 unit tests**.

Security collector tests use mocked registry and PowerShell data. Real-hardware validation remains ongoing.

## 🏗️ Architecture

\`\`\`text
ITOps-Command/
│
├── gui.py
│
├── modules/
│   ├── inventory.py
│   ├── network.py
│   ├── processes.py
│   ├── health.py
│   ├── root_cause.py
│   ├── fix_plan.py
│   ├── fix_engine.py
│   ├── security.py
│   ├── security_fix.py
│   ├── registry_io.py
│   ├── history.py
│   ├── export.py
│   ├── win_silent.py
│   ├── paths.py
│   └── version.py
│
├── tests/
├── docs/
├── build_exe.bat
├── run_gui.bat
├── run_gui.vbs
├── requirements.txt
├── CHANGELOG.md
└── LICENSE
\`\`\`

## ⚠️ Known Limitations

ITOps Command is currently in Beta.

- Broader Windows 10/11 real-device validation is ongoing.
- Some PowerShell and registry collectors need validation across different Windows builds.
- Parts of network diagnostics still depend on localized command output.
- ICMP gateway checks may report false reachability issues.
- Captive portals can affect connectivity results.
- Health score and security score measure different things.
- History currently stores only the previous snapshot.
- Security remediation GUI is not yet implemented.
- Executable code signing is planned.

## 🗺️ Roadmap

| Priority | Planned Feature |
|---|---|
| High | Real-hardware validation |
| High | Improved security assessment interface |
| High | Remediation approval and rollback GUI |
| Medium | Locale-independent network diagnostics |
| Medium | PDF and advanced reporting |
| Medium | SQLite diagnostic history |
| Future | Installer and code signing |
| Future | Multi-device / MSP management |

*Roadmap items are planned, not currently available features.*

## 🔐 Privacy & Security

- No account required.
- No built-in telemetry upload.
- Reports stored locally.
- Security scans are read-only.
- Remediation is opt-in.
- External connectivity probes are used only for reachability checks.

Always review organisational policies before using the tool on managed endpoints.

## 🤝 Feedback

Found an issue or compatibility problem?

Open a GitHub issue with:
- Windows version and build.
- Application privilege level.
- Relevant finding ID.
- Sanitized debug output.

Never upload passwords, credentials, tokens, or sensitive endpoint information.

## 📄 License

**Proprietary — All Rights Reserved.**

Public repository visibility does not grant permission for commercial use, redistribution, or modification. See [LICENSE](LICENSE).

## 👨‍💻 Maintainer

**Asem Dief**

[GitHub Profile](https://github.com/Asemdief)

---

<div align="center">

### ITOps Command

**Less Guesswork. Better Endpoint Visibility.**

</div>

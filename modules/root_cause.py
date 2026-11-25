"""Root cause analysis from collected data."""

from __future__ import annotations


def analyze_root_cause(data: dict) -> dict:
    issues: list[str] = []
    suggestions: list[str] = []

    for d in data.get("disk") or []:
        pct = float(d.get("usage_percent") or 0)
        dev = d.get("device", "Drive")
        if pct >= 85:
            issues.append(f"High disk usage on {dev}")
            suggestions.append(f"Clean temporary files and large folders on {dev}")
        elif pct >= 70:
            issues.append(f"Elevated disk usage on {dev}")
            suggestions.append(f"Monitor free space on {dev} and remove unused files")

    cpu = data.get("cpu") or {}
    if float(cpu.get("usage_percent") or 0) >= 85:
        issues.append("High CPU usage")
        suggestions.append("Close heavy applications or check background processes")

    ram = data.get("ram") or {}
    if float(ram.get("usage_percent") or 0) >= 90:
        issues.append("High memory pressure")
        suggestions.append("Close unused apps or add RAM if this is frequent")

    net = data.get("network") or {}
    if not net.get("internet_ok"):
        issues.append("Internet connectivity issue")
        suggestions.append("Check ISP or physical connection")
    elif not net.get("gateway_ok"):
        issues.append("Gateway connectivity issue")
        suggestions.append("Check router / local gateway")
    elif not net.get("dns_ok"):
        issues.append("DNS resolution issue")
        suggestions.append("Flush DNS or try alternate DNS servers")

    if not issues:
        return {"status": "Healthy", "issues": [], "suggestions": []}
    if len(issues) >= 2:
        status = "Multiple Issues Detected"
    else:
        status = "Minor Issues"
    return {"status": status, "issues": issues, "suggestions": suggestions}

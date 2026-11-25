"""
Safe auto-fix — ALL actions silent (no CMD / PowerShell window).
Never launches cleanmgr or any visible UI.

Safety contract (v1.10):
  * TEMP cleanup only touches items whose newest file is older than
    MIN_AGE_HOURS — nothing a running app or installer may still be using.
  * Emptying the Recycle Bin is irreversible user-data loss, so it is NOT run
    automatically. The function remains for an explicit, user-confirmed action.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import time
from pathlib import Path

from modules.win_silent import run_powershell, run_silent


def _ok(action: str, details: str) -> dict:
    return {"action": action, "success": True, "details": details}


def _fail(action: str, details: str) -> dict:
    return {"action": action, "success": False, "details": details}


MIN_AGE_HOURS = 24
MAX_ITEMS = 2000
_MAX_WALK = 5000


def _newest_mtime(path: Path) -> float:
    """Newest modification time anywhere under `path`. Huge trees count as 'recent'."""
    try:
        newest = path.lstat().st_mtime
    except OSError:
        return time.time()
    seen = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for name in dirnames + filenames:
            seen += 1
            if seen > _MAX_WALK:
                return time.time()  # too large to judge safely -> leave it alone
            try:
                newest = max(newest, os.lstat(os.path.join(dirpath, name)).st_mtime)
            except OSError:
                pass
    return newest


def clean_user_temp(
    root: str | None = None,
    *,
    min_age_hours: float = MIN_AGE_HOURS,
    now: float | None = None,
) -> dict:
    action = "Clean user TEMP folder"
    temp = root or os.environ.get("TEMP") or tempfile.gettempdir()
    cutoff = (time.time() if now is None else now) - min_age_hours * 3600
    deleted = kept_recent = skipped = 0
    try:
        base = Path(temp)
        if not base.is_dir():
            return _fail(action, f"TEMP not found: {temp}")
        for item in list(base.iterdir())[:MAX_ITEMS]:
            try:
                if item.is_symlink() or item.is_file():
                    if item.lstat().st_mtime > cutoff:
                        kept_recent += 1
                        continue
                    item.unlink(missing_ok=True)
                    deleted += 1
                elif item.is_dir():
                    if _newest_mtime(item) > cutoff:
                        kept_recent += 1
                        continue
                    shutil.rmtree(item, ignore_errors=True)
                    if item.exists():
                        skipped += 1
                    else:
                        deleted += 1
            except OSError:
                skipped += 1
        return _ok(
            action,
            f"Deleted {deleted} items older than {min_age_hours:g}h "
            f"(kept {kept_recent} recent, skipped {skipped} locked)",
        )
    except Exception as e:
        return _fail(action, str(e))


def flush_dns() -> dict:
    action = "Flush DNS cache"
    try:
        r = run_silent(["ipconfig", "/flushdns"], timeout=20)
        out = (r.stdout or r.stderr or "").strip() or "DNS cache flushed"
        return _ok(action, out[:240]) if r.returncode == 0 else _fail(action, out[:240])
    except Exception as e:
        return _fail(action, str(e))


def empty_recycle_bin() -> dict:
    """Irreversible. NOT called by run_auto_fixes — only for an explicit user action."""
    action = "Empty Recycle Bin"
    try:
        script = (
            "$ErrorActionPreference='SilentlyContinue'; "
            "Clear-RecycleBin -Force -ErrorAction SilentlyContinue; "
            "'Recycle Bin cleared'"
        )
        r = run_powershell(script, timeout=45)
        out = (r.stdout or r.stderr or "").strip() or "Done"
        if r.returncode == 0:
            return _ok(action, out[:200])
        return _fail(action, out[:200] or "Failed (may need Admin or already empty)")
    except Exception as e:
        return _fail(action, str(e))


def clear_dns_client_cache() -> dict:
    action = "Clear DNS client cache"
    try:
        r = run_powershell("Clear-DnsClientCache -ErrorAction SilentlyContinue; 'OK'", timeout=20)
        if r.returncode == 0:
            return _ok(action, "DNS client cache cleared")
        return _fail(action, (r.stderr or r.stdout or "failed")[:200])
    except Exception as e:
        return _fail(action, str(e))


def run_auto_fixes(root_cause: dict | None = None) -> list[dict]:
    results: list[dict] = []
    issues = []
    status = ""
    if isinstance(root_cause, dict):
        issues = [str(x).lower() for x in (root_cause.get("issues") or [])]
        status = str(root_cause.get("status", "")).lower()

    results.append(clean_user_temp())
    results.append(flush_dns())

    need_net = any(
        x in i for i in issues for x in ("internet", "network", "dns", "gateway", "connectivity")
    ) or ("issue" in status and "healthy" not in status)

    if need_net:
        results.append(clear_dns_client_cache())

    return results

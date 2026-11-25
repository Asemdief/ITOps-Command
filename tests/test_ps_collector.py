"""Regression tests from the first real-Windows run: PowerShell JSON arrived with a UTF-8 BOM,
every PowerShell-backed check silently turned UNKNOWN, and startup entries were reported 'trusted'
without any signature lookup."""
import json
import subprocess
import unittest
from unittest import mock

from modules import security as S
from tests.test_security import GOOD_PS, NOW, FakeReg, by_id, hardened_reg, scan

BOM = "\ufeff"


def cp(stdout, rc=0, stderr=""):
    return subprocess.CompletedProcess([], rc, stdout=stdout, stderr=stderr)


PAYLOADS = {
    "protection": {"defender": {"ok": True, "rtp": True, "sigAge": 1, "tamper": True}, "av": ["Windows Defender"]},
    "accounts": {"admins": ["PC\\me"], "users": [{"sid": "S-1-5-21-1-501", "name": "Guest", "enabled": False}], "bitlocker": 1},
    "patch": {"lastHotfix": "2026-11-05"},
}


def fake_ps(prefix="", overrides=None):
    overrides = overrides or {}

    def run(script, *, timeout=60, encoding=None):
        part = script.split("\n", 1)[0].replace("# part:", "").strip()
        if part in overrides:
            return overrides[part]
        return cp(prefix + json.dumps(PAYLOADS[part]))
    return run


class TestExtractJson(unittest.TestCase):
    def test_bom_prefixed_output_parses(self):
        self.assertEqual(S._extract_json(BOM + '{"a":1}'), {"a": 1})

    def test_noise_before_payload_is_ignored(self):
        self.assertEqual(S._extract_json('WARNING: something\r\n' + BOM + '{"a":[1,2]}\r\n'), {"a": [1, 2]})

    def test_no_json_raises(self):
        with self.assertRaises(ValueError):
            S._extract_json("nothing here")


class TestCollect(unittest.TestCase):
    def test_bom_output_still_yields_data(self):
        with mock.patch("modules.win_silent.run_powershell", fake_ps(prefix=BOM)):
            d = S.collect_ps(admin=False)
        self.assertEqual(d["_errors"], {})
        self.assertTrue(d["defender"]["rtp"])
        self.assertEqual(d["lastHotfix"], "2026-11-05")
        self.assertNotIn("_error", d)

    def test_one_slow_part_does_not_take_down_the_others(self):
        with mock.patch("modules.win_silent.run_powershell", fake_ps(overrides={"patch": cp("", rc=124, stderr="timeout")})):
            d = S.collect_ps(admin=False)
        self.assertIn("patch", d["_errors"])
        self.assertIn("timed out", d["_errors"]["patch"])
        self.assertTrue(d["defender"]["rtp"])  # protection part survived
        r = scan(hardened_reg(), d)
        self.assertEqual(by_id(r, "ITC-001")["status"], "PASS")
        f = by_id(r, "ITC-050")
        self.assertEqual(f["status"], "UNKNOWN")
        self.assertIn("timed out", f["evidence"])  # the UI can show WHY

    def test_all_parts_failing_sets_global_error_and_reasons_are_visible(self):
        bad = {k: cp("garbage", rc=1, stderr="boom") for k in PAYLOADS}
        with mock.patch("modules.win_silent.run_powershell", fake_ps(overrides=bad)):
            d = S.collect_ps(admin=True)
        self.assertIn("_error", d)
        r = scan(hardened_reg(), d)
        self.assertEqual(by_id(r, "ITC-001")["status"], "UNKNOWN")
        self.assertIn("PowerShell", by_id(r, "ITC-001")["evidence"])
        self.assertTrue(r["collector_errors"])

    def test_admin_adds_exclusions_query(self):
        seen = []
        def run(script, *, timeout=60, encoding=None):
            seen.append(script)
            return fake_ps()(script, timeout=timeout)
        with mock.patch("modules.win_silent.run_powershell", run):
            S.collect_ps(admin=True)
            admin_scripts = [x for x in seen if "Get-MpPreference" in x]
            seen.clear()
            S.collect_ps(admin=False)
        self.assertEqual(len(admin_scripts), 1)
        self.assertFalse(any("Get-MpPreference" in x for x in seen))

    def test_signatures_parse_with_bom(self):
        out = BOM + json.dumps([{"path": "C:\\a.exe", "status": "Valid", "signer": "CN=X"}])
        with mock.patch("modules.win_silent.run_powershell", lambda *a, **k: cp(out)):
            r = S.check_signatures(["C:\\a.exe"])
        self.assertEqual(r["C:\\a.exe"]["status"], "Valid")


class TestHonestScoring(unittest.TestCase):
    def test_startup_is_unknown_not_trusted_when_signatures_unavailable(self):
        reg = hardened_reg()
        reg.runs = {("HKCU", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"): {"App": r'"C:\Program Files\App\a.exe"'}}
        r = S.run_security_scan(reg=reg, ps_data=GOOD_PS, admin=True, now=NOW,
                                signatures=lambda p: None, listeners=lambda: [])
        self.assertEqual(by_id(r, "ITC-060")["status"], "UNKNOWN")

    def test_startup_risky_path_still_warns_without_signatures(self):
        reg = hardened_reg()
        reg.runs = {("HKCU", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"): {"X": r'"C:\Users\u\Downloads\x.exe"'}}
        r = S.run_security_scan(reg=reg, ps_data=GOOD_PS, admin=True, now=NOW,
                                signatures=lambda p: None, listeners=lambda: [])
        self.assertEqual(by_id(r, "ITC-060")["status"], "WARN")

    def test_low_coverage_gets_no_letter_grade(self):
        # Exactly the first real run: registry checks pass, everything PowerShell-backed is UNKNOWN.
        r = scan(hardened_reg(), {"_error": "all parts failed"}, admin=False)
        self.assertLess(r["coverage"]["percent"], 70)
        self.assertTrue(r["provisional"])
        self.assertEqual(r["grade"], "N/A")
        self.assertIn("PROVISIONAL", S.format_text(r))

    def test_full_coverage_keeps_grade(self):
        r = scan(hardened_reg(), GOOD_PS)
        self.assertFalse(r["provisional"])
        self.assertEqual(r["grade"], "A")


if __name__ == "__main__":
    unittest.main()

import unittest

from modules.fix_plan import generate_fix_plan
from modules.root_cause import analyze_root_cause
from modules.version import __version__


class TestCore(unittest.TestCase):
    def test_disk_fix_names_the_actual_drive_not_hardcoded_letters(self):
        data = {"disk": [{"device": "G:\\", "usage_percent": 93}],
                "cpu": {"usage_percent": 10}, "ram": {"usage_percent": 40},
                "network": {"internet_ok": True, "gateway_ok": True, "dns_ok": True}}
        plan = generate_fix_plan(analyze_root_cause(data))
        self.assertIn("G:", plan[0]["fix"])
        self.assertNotIn("D:", plan[0]["fix"])

    def test_healthy_machine_has_no_issues(self):
        data = {"disk": [{"device": "C:\\", "usage_percent": 40}], "cpu": {"usage_percent": 5},
                "ram": {"usage_percent": 30}, "network": {"internet_ok": True, "gateway_ok": True, "dns_ok": True}}
        self.assertEqual(analyze_root_cause(data)["status"], "Healthy")

    def test_version_is_semver(self):
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+$")


if __name__ == "__main__":
    unittest.main()

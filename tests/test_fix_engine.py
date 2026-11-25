import os, shutil, tempfile, time, unittest
from unittest import mock

from modules import fix_engine as FE

H = 3600


def touch(path, age_hours):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("x")
    t = time.time() - age_hours * H
    os.utime(path, (t, t))


class TestTempCleanup(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def p(self, *a):
        return os.path.join(self.d, *a)

    def test_old_deleted_recent_kept(self):
        touch(self.p("old.tmp"), 72)
        touch(self.p("new.tmp"), 1)
        r = FE.clean_user_temp(self.d)
        self.assertTrue(r["success"])
        self.assertFalse(os.path.exists(self.p("old.tmp")))
        self.assertTrue(os.path.exists(self.p("new.tmp")))

    def test_old_dir_with_recent_file_inside_is_kept(self):
        touch(self.p("installer", "setup.log"), 0.1)       # active write
        old = time.time() - 100 * H
        os.utime(self.p("installer"), (old, old))            # dir itself looks old
        FE.clean_user_temp(self.d)
        self.assertTrue(os.path.exists(self.p("installer", "setup.log")))

    def test_fully_old_dir_is_removed(self):
        touch(self.p("cache", "a", "b.bin"), 200)
        old = time.time() - 200 * H
        for d in (self.p("cache", "a"), self.p("cache")):
            os.utime(d, (old, old))
        FE.clean_user_temp(self.d)
        self.assertFalse(os.path.exists(self.p("cache")))

    def test_missing_dir_reports_failure_not_crash(self):
        self.assertFalse(FE.clean_user_temp(self.p("nope"))["success"])

    def test_recycle_bin_never_runs_automatically(self):
        with mock.patch.object(FE, "empty_recycle_bin") as rb, \
             mock.patch.object(FE, "clean_user_temp", return_value={"success": True}), \
             mock.patch.object(FE, "flush_dns", return_value={"success": True}):
            FE.run_auto_fixes({"issues": ["High disk usage on C:", "Low disk space"], "status": "critical"})
            rb.assert_not_called()


if __name__ == "__main__":
    unittest.main()

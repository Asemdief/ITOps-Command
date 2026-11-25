import os
import sys


def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    modules_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(modules_dir)


def get_data_dir():
    """Per-user writable data dir (safe even when installed in Program Files)."""
    base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".itops-command")
    d = os.path.join(base, "ITOpsCommand")
    os.makedirs(d, exist_ok=True)
    return d

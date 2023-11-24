import sys
from pathlib import PosixPath, WindowsPath

if sys.platform == "win32":
    path_type = WindowsPath
else:
    path_type = PosixPath


class AssetsPath(path_type):
    """Custom path for settings that can be absolute or relative to `assets_dir`."""


class WorkPath(path_type):
    """Custom path for settings that can be absolute or relative to `work_dir`."""

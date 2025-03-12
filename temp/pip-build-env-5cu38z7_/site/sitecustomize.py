
import os, site, sys

# First, drop system-sites related paths.
original_sys_path = sys.path[:]
known_paths = set()
for path in {'/usr/local/lib64/python3.12/site-packages', '/usr/lib64/python3.12/site-packages', '/usr/lib/python3.12/site-packages', '/usr/local/lib/python3.12/site-packages'}:
    site.addsitedir(path, known_paths=known_paths)
system_paths = set(
    os.path.normcase(path)
    for path in sys.path[len(original_sys_path):]
)
original_sys_path = [
    path for path in original_sys_path
    if os.path.normcase(path) not in system_paths
]
sys.path = original_sys_path

# Second, add lib directories.
# ensuring .pth file are processed.
for path in ['/root/WatchTower/pip-build-env-5cu38z7_/overlay/lib/python3.12/site-packages', '/root/WatchTower/pip-build-env-5cu38z7_/overlay/lib64/python3.12/site-packages', '/root/WatchTower/pip-build-env-5cu38z7_/normal/lib/python3.12/site-packages', '/root/WatchTower/pip-build-env-5cu38z7_/normal/lib64/python3.12/site-packages']:
    assert not path in sys.path
    site.addsitedir(path)

import os
import pwd
import tempfile
from dataclasses import dataclass
from typing import List, cast
from unittest import mock

import shellmarks
from shellmarks import ModuleParams, OptionalModuleParams, ShellmarkManager

TEST_PATH = os.path.abspath(os.path.join("tests", "files"))
DIR1 = os.path.join(TEST_PATH, "dir1")
DIR2 = os.path.join(TEST_PATH, "dir2")
DIR3 = os.path.join(TEST_PATH, "dir3")
HOME_DIR = pwd.getpwuid(os.getuid()).pw_dir

# Paths in this file have to be absolute paths. The path depends on the
# location of the repository.
sdirs_file = open(os.path.join(TEST_PATH, "sdirs"), "w")
sdirs_file.write(
    'export DIR_dir1="{}"\nexport DIR_dir2="{}"\nexport DIR_dir3="{}"\n'.format(
        DIR1, DIR2, DIR3
    )
)
sdirs_file.close()


def create_tmp_text_file_with_content(content: str) -> str:
    path = tmp_file()
    file_handler = open(path, "w")
    file_handler.write(content)
    file_handler.close()
    return path


def tmp_file() -> str:
    return tempfile.mkstemp()[1]


def tmp_dir() -> str:
    return tempfile.mkdtemp()


def read(sdirs: str) -> List[str]:
    return open(sdirs, "r").readlines()


def create_sdirs(config: list[tuple[str, str]]) -> ShellmarkManager:
    sdirs = tmp_file()

    entries = ShellmarkManager(path=sdirs)

    for entry in config:
        entries.add_entry(mark=entry[0], path=entry[1], validate=False)
    entries.write()

    return entries


@dataclass
class MockResult:
    module: mock.MagicMock
    AnsibleModule: mock.MagicMock
    params: ModuleParams
    manager: ShellmarkManager


def mock_main(params: OptionalModuleParams, check_mode: bool = False) -> MockResult:
    sdirs = tmp_file()
    defaults = {
        "cleanup": False,
        "delete_duplicates": False,
        "export": None,
        "export_query": None,
        "mark": None,
        "path": None,
        "replace_home": False,
        "sdirs": sdirs,
        "sorted": False,
        "state": "present",
    }

    for key, value in list(defaults.items()):
        if key not in params:
            params[key] = value  # type: ignore

    p = cast(ModuleParams, params)

    with mock.patch("shellmarks.AnsibleModule") as AnsibleModule:
        module = AnsibleModule.return_value
        module.params = params
        module.check_mode = check_mode
        shellmarks.main()

    entries = ShellmarkManager(path=p["sdirs"])

    return MockResult(
        module=module,
        AnsibleModule=AnsibleModule,
        params=p,
        manager=entries,
    )

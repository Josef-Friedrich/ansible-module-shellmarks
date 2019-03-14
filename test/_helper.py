# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division)
import tempfile
import pwd
import os
import mock
import shellmarks


TEST_PATH = os.path.abspath(os.path.join('test', 'files'))
DIR1 = os.path.join(TEST_PATH, 'dir1')
DIR2 = os.path.join(TEST_PATH, 'dir2')
DIR3 = os.path.join(TEST_PATH, 'dir3')
HOME_DIR = pwd.getpwuid(os.getuid()).pw_dir

# Paths in this file have to be absolute paths. The path depends on the
# location of the repository.
sdirs_file = open(os.path.join(TEST_PATH, 'sdirs'), 'w')
sdirs_file.write(
    'export DIR_dir1="{}"\nexport DIR_dir2="{}"\nexport DIR_dir3="{}"\n'
    .format(DIR1, DIR2, DIR3)
)
sdirs_file.close()


def create_tmp_text_file_with_content(content):
    path = tmp_file()
    file_handler = open(path, 'w')
    file_handler.write(content)
    file_handler.close()
    return path


def tmp_file():
    return tempfile.mkstemp()[1]


def tmp_dir():
    return tempfile.mkdtemp()


def read(sdirs):
    return open(sdirs, 'r').readlines()


def mock_main(params, check_mode=False):
    sdirs = tmp_file()
    defaults = {
        "cleanup": False,
        "delete_duplicates": False,
        "mark": False,
        "path": False,
        "replace_home": True,
        "sdirs": sdirs,
        "sorted": False,
        "state": "present",
    }

    for key, value in list(defaults.items()):
        if key not in params:
            params[key] = value

    with mock.patch('shellmarks.AnsibleModule') as AnsibleModule:
        module = AnsibleModule.return_value
        module.params = params
        module.check_mode = check_mode
        shellmarks.main()

    return module

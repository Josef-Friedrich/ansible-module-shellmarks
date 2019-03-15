# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division)
from ansible.compat.tests import unittest
import mock

from _helper import \
    DIR1, \
    HOME_DIR, \
    mock_main, \
    read, \
    tmp_file


class TestFunctionalWithMockErrors(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.module = False
        cls.entries = False
        cls.sdirs = tmp_file()

    def mock_add(self, mark, path):
        mock_objects = mock_main(
            params={'mark': mark, 'path': path, 'sdirs': self.sdirs},
            check_mode=False
        )
        self.module = mock_objects['module']
        self.entries = mock_objects['entries']
        return mock

    def test_error_dash(self):
        self.mock_add(mark='l-l', path=DIR1)
        self.module.fail_json.assert_called_with(
            msg='Invalid mark string: “l-l”. Allowed characters for bookmark '
            'names are: “0-9a-zA-Z_”.'
        )

    def test_error_blank_space(self):
        self.mock_add(mark='l l', path=DIR1)
        self.module.fail_json.assert_called_with(
            msg='Invalid mark string: “l l”. Allowed characters for bookmark '
            'names are: “0-9a-zA-Z_”.'
        )

    def test_error_umlaut(self):
        self.mock_add(mark='löl', path=DIR1)
        self.module.fail_json.assert_called_with(
            msg='Invalid mark string: “löl”. Allowed characters for bookmark '
            'names are: “0-9a-zA-Z_”.'
        )

    def test_error_comma(self):
        self.mock_add(mark='l,l', path=DIR1)
        self.module.fail_json.assert_called_with(
            msg='Invalid mark string: “l,l”. Allowed characters for bookmark '
            'names are: “0-9a-zA-Z_”.'
        )


class TestFunction(unittest.TestCase):

    def test_mock(self):
        sdirs = tmp_file()
        mock_objects = mock_main({
            'cleanup': False,
            'delete_duplicates': False,
            'mark': 'dir1',
            'path': DIR1,
            'replace_home': True,
            'sdirs': sdirs,
            'sorted': False,
            'state': 'present',
        }, check_mode=False)

        expected = dict(
            cleanup=dict(default=False, type='bool'),
            delete_duplicates=dict(default=False, type='bool'),
            mark=dict(aliases=['bookmark']),
            path=dict(aliases=['src']),
            replace_home=dict(default=True, type='bool'),
            sdirs=dict(default='~/.sdirs'),
            sorted=dict(default=True, type='bool'),
            state=dict(default='present', choices=['present', 'absent']),
        )

        assert(
            mock.call(
                argument_spec=expected,
                supports_check_mode=True
            ) == mock_objects['AnsibleModule'].call_args
        )

        lines = read(sdirs)
        result_path = DIR1.replace(HOME_DIR, '$HOME')
        self.assertEqual(
            lines[0],
            'export DIR_dir1="{}"\n'.format(result_path)
        )

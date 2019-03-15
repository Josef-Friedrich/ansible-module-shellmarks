# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division)
from ansible.compat.tests import unittest
import mock
from shellmarks import ShellmarkEntries

from _helper import \
    create_tmp_text_file_with_content, \
    DIR1, \
    DIR2, \
    DIR3, \
    HOME_DIR, \
    mock_main, \
    read, \
    tmp_dir, \
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


class TestFunctionalWithMock(unittest.TestCase):

    @staticmethod
    def create_sdirs_file():
        content = 'export DIR_dirB="{}"\n' + \
            'export DIR_dirC="{}"\n' + \
            'export DIR_dirA="{}"\n'
        content = content.format(DIR2, DIR3, DIR1)
        return create_tmp_text_file_with_content(content)

    def test_present(self):
        mock_objects = mock_main(params={'path': DIR1, 'mark': 'tmp'})
        self.assertEqual(len(mock_objects['entries'].entries), 1)
        entry = mock_objects['entries'].get_entry_by_index(0)
        self.assertEqual(entry.mark, 'tmp')
        self.assertEqual(entry.path, DIR1)

    def test_sort(self):
        # With check mode enabled
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(params={'sorted': True, 'sdirs': sdirs},
                                 check_mode=True)
        self.assertEqual(mock_objects['entries'].entries[0].mark, 'dirB')
        mock_objects['module'].exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    'action': 'sort',
                    'sort_by': 'mark',
                    'reverse': False,
                },
            ]
        )

        # Sort
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(params={'sorted': True, 'sdirs': sdirs},
                                 check_mode=False)
        self.assertEqual(mock_objects['entries'].entries[0].mark, 'dirA')
        self.assertEqual(mock_objects['entries'].entries[1].mark, 'dirB')
        self.assertEqual(mock_objects['entries'].entries[2].mark, 'dirC')
        self.assertEqual(mock_objects['entries'].entries[2].mark, 'dirC')
        mock_objects['module'].exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    'action': 'sort',
                    'sort_by': 'mark',
                    'reverse': False,
                },
            ]
        )

        # Sort not
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(params={'sorted': False, 'sdirs': sdirs},
                                 check_mode=False)
        self.assertEqual(mock_objects['entries'].entries[0].mark, 'dirB')
        self.assertEqual(mock_objects['entries'].entries[1].mark, 'dirC')
        self.assertEqual(mock_objects['entries'].entries[2].mark, 'dirA')
        mock_objects['module'].exit_json.assert_called_with(
            changed=False
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

    def test_delete(self):
        mock_objects = mock_main({
            'state': 'absent',
            'delete_duplicates': False,
            'path': '/tmp',
            'mark': 'tmp',
            'sorted': False,
            'cleanup': False,
        }, check_mode=False)

        args = mock_objects['module'].exit_json.call_args
        self.assertEqual(mock.call(changed=False), args)


class TestFunctionalWithMockDeletion(unittest.TestCase):

    def setUp(self):
        self.sdirs = tmp_file()
        self.mock_add('tmp1', DIR1)
        self.mock_add('tmp2', DIR2)
        self.mock_add('tmp3', DIR3)

    def mock_add(self, mark, path):
        return mock_main(
            params={'mark': mark, 'path': path, 'sdirs': self.sdirs},
            check_mode=False
        )

    def test_delete_by_mark(self):
        mock_objects = mock_main({
            'sdirs': self.sdirs,
            'mark': 'tmp1',
            'state': 'absent',
        })
        self.assertEqual(len(mock_objects['entries'].entries), 2)
        mock_objects['module'].exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    'action': 'delete',
                    'mark': 'tmp1',
                    'path': DIR1
                },
            ]
        )

    def test_delete_nonexistent(self):
        non_existent = '/tmp/tmp34723423643646346etfjf34gegf623646'
        mock_objects = mock_main({
            'sdirs': self.sdirs,
            'path': non_existent,
            'state': 'absent'})
        self.assertEqual(len(mock_objects['entries'].entries), 3)
        mock_objects['module'].exit_json.assert_called_with(
            changed=False
        )

    def test_delete_by_path(self):
        mock_objects = mock_main({
            'sdirs': self.sdirs,
            'path': DIR1,
            'state': 'absent'
        })
        self.assertEqual(len(mock_objects['entries'].entries), 2)
        mock_objects['module'].exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    'action': 'delete',
                    'mark': 'tmp1',
                    'path': DIR1
                },
            ]
        )

    def test_delete_by_path_and_mark(self):
        mock_objects = mock_main({
            'sdirs': self.sdirs,
            'mark': 'tmp1',
            'path': DIR1,
            'state': 'absent'
        })
        self.assertEqual(len(mock_objects['entries'].entries), 2)
        mock_objects['module'].exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    'action': 'delete',
                    'mark': 'tmp1',
                    'path': DIR1
                },
            ]
        )

    def test_delete_casesensitivity(self):
        mock_objects = mock_main({
            'sdirs': self.sdirs,
            'mark': 'TMP1',
            'state': 'absent'
        })
        self.assertEqual(len(mock_objects['entries'].entries), 3)
        mock_objects['module'].exit_json.assert_called_with(
            changed=False
        )

    def test_delete_on_empty_sdirs_by_mark(self):
        mock_objects = mock_main({
            'sdirs': tmp_file(),
            'mark': 'dir1',
            'state': 'absent'
        })
        mock_objects['module'].exit_json.assert_called_with(
            changed=False
        )

    def test_delete_on_empty_sdirs_by_path(self):
        mock_objects = mock_main({
            'sdirs': tmp_file(),
            'path': '/dir1',
            'state': 'absent'
        })
        mock_objects['module'].exit_json.assert_called_with(
            changed=False
        )

    def test_delete_on_empty_sdirs_by_path_and_mark(self):
        mock_objects = mock_main({
            'sdirs': tmp_file(),
            'mark': 'dir1',
            'path': '/dir1',
            'state': 'absent'
        })
        mock_objects['module'].exit_json.assert_called_with(
            changed=False
        )


class TestFunctionWithMockCleanUp(unittest.TestCase):

    def test_cleanup(self):
        path = tmp_dir()
        no = 'export DIR_tmpb="/tmpXDR34723df4WER/d4REd4RE64er64erb"\n'
        content = no + no + no + \
            'export DIR_exists="' + path + '"\n' + no + no + no
        sdirs = create_tmp_text_file_with_content(content)

        mock_objects = mock_main({
            'cleanup': True,
            'sdirs': sdirs
        })
        self.assertEqual(len(mock_objects['entries'].entries), 1)
        self.assertEqual(mock_objects['entries'].entries[0].path, path)

        mock_objects['module'].exit_json.assert_called_with(
            changed=True,
            changes=[{'action': 'cleanup', 'count': 6}]
        )

    def test_nothing_to_do(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark='dir1', path=DIR1)
        entries.add_entry(mark='dir2', path=DIR2)
        entries.add_entry(mark='dir3', path=DIR3)
        entries.write()

        mock_objects = mock_main({
            'cleanup': True,
            'sdirs': entries.path
        })

        entries = ShellmarkEntries(path=mock_objects['module'].params['sdirs'])
        self.assertEqual(len(mock_objects['entries'].entries), 3)
        self.assertEqual(mock_objects['entries'].entries[0].path, DIR1)

        mock_objects['module'].exit_json.assert_called_with(
            changed=False
        )

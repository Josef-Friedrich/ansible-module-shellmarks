# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division)
import tempfile
import pwd
import os
from ansible.compat.tests import unittest
import mock
import shellmarks
from shellmarks import Entry, ShellmarkEntries, MarkInvalidError, NoPathError

__metaclass__ = type

TEST_PATH = os.path.abspath(os.path.join('test', 'files'))
DIR1 = os.path.join(TEST_PATH, 'dir1')
DIR2 = os.path.join(TEST_PATH, 'dir2')
DIR3 = os.path.join(TEST_PATH, 'dir3')


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
        "mark": False,
        "path": False,
        "replace_home": True,
        "sdirs": sdirs,
        "sorted": True,
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


class TestFunctionalWithMockErrors(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.module = False
        cls.entries = False
        cls.sdirs = tmp_file()

    def mock_add(self, mark, path):
        module = mock_main(
            params={'mark': mark, 'path': path, 'sdirs': self.sdirs},
            check_mode=False
        )
        self.module = module
        self.entries = ShellmarkEntries(path=module.params['sdirs'])
        return module

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
        module = mock_main(params={'path': DIR1, 'mark': 'tmp'})
        sdirs = module.params['sdirs']
        entries = ShellmarkEntries(path=sdirs)
        self.assertEqual(len(entries.entries), 1)
        entry = entries.get_entry_by_index(0)
        self.assertEqual(entry.mark, 'tmp')
        self.assertEqual(entry.path, DIR1)

    @unittest.skip('Fix later')
    def test_sort(self):
        # With check mode enabled
        sdirs = self.create_sdirs_file()
        module = mock_main(params={'sorted': True, 'sdirs': sdirs},
                           check_mode=True)
        entries = ShellmarkEntries(path=sdirs)
        self.assertEqual(entries.entries[0].mark, 'dirB')
        # TODO: msg?
        module.exit_json.assert_called_with(changed=True, msg='')

        # Sort
        sdirs = self.create_sdirs_file()
        module = mock_main(params={'sorted': True, 'sdirs': sdirs},
                           check_mode=False)
        entries = ShellmarkEntries(path=sdirs)
        self.assertEqual(entries.entries[0].mark, 'dirA')
        self.assertEqual(entries.entries[1].mark, 'dirB')
        self.assertEqual(entries.entries[2].mark, 'dirC')
        self.assertEqual(entries.entries[2].mark, 'dirC')
        # TODO: msg?
        module.exit_json.assert_called_with(changed=True, msg='')

        # Sort not
        sdirs = self.create_sdirs_file()
        module = mock_main(params={'sorted': False, 'sdirs': sdirs},
                           check_mode=False)
        entries = ShellmarkEntries(path=sdirs)
        self.assertEqual(entries.entries[0].mark, 'dirB')
        self.assertEqual(entries.entries[1].mark, 'dirC')
        self.assertEqual(entries.entries[2].mark, 'dirA')
        # TODO: changed=True is wrong, msg?
        # module.exit_json.assert_called_with(changed=False, msg='')


class TestFunction(unittest.TestCase):

    @unittest.skip('Fix later')
    @mock.patch("shellmarks.AnsibleModule")
    def test_mock(self, AnsibleModule):
        sdirs = tmp_file()
        module = AnsibleModule.return_value
        module.params = {
            'state': 'present',
            'path': '/tmp',
            'mark': 'tmp',
            'sdirs': sdirs
        }
        module.check_mode = False
        shellmarks.main()

        expected = dict(
            cleanup=dict(default=False, type='bool'),
            mark=dict(aliases=['bookmark']),
            path=dict(aliases=['src']),
            replace_home=dict(default=True, type='bool'),
            sdirs=dict(default='~/.sdirs'),
            sorted=dict(default=True, type='bool'),
            state=dict(default='present', choices=['present', 'absent']),
        )

        assert(mock.call(argument_spec=expected,
               supports_check_mode=True) == AnsibleModule.call_args)

        lines = read(sdirs)
        self.assertEqual(lines[0], 'export DIR_tmp="/tmp"\n')

    @unittest.skip('Fix later')
    @mock.patch("shellmarks.AnsibleModule")
    def test_delete(self, AnsibleModule):
        sdirs = tmp_file()
        module = AnsibleModule.return_value
        module.params = {
            'state': 'absent',
            'path': '/tmp',
            'mark': 'tmp',
            'sdirs': sdirs
        }
        module.check_mode = False
        shellmarks.main()

        args = module.exit_json.call_args
        self.assertEqual(mock.call(changed=False, msg='tmp : /tmp'), args)


class TestFunctionalWithMockAdd(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sdirs = tmp_file()

    def mock_add(self, mark, path):
        return mock_main(
            params={'mark': mark, 'path': path, 'sdirs': self.sdirs},
            check_mode=False
        )

    @unittest.skip('Fix later')
    def test_add(self):
        module = self.mock_add('tmp1', DIR1)
        entries = ShellmarkEntries(path=module.params['sdirs'])
        self.assertEqual(len(entries.entries), 1)
        # TODO rewrite
        # self.assertEqual(sm.skipped, False)
        module.exit_json.assert_called_with(
            changed=True,
            msg='tmp1 : {}'.format(DIR1)
        )

        # same entry
        module = self.mock_add('tmp1', DIR1)
        entries = ShellmarkEntries(path=module.params['sdirs'])
        self.assertEqual(len(entries.entries), 1)
        module.exit_json.assert_called_with(
            changed=False,
            msg='tmp1 : {}'.format(DIR1)
        )

        # same mark
        module = self.mock_add('tmp1', DIR2)
        entries = ShellmarkEntries(path=module.params['sdirs'])
        self.assertEqual(len(entries.entries), 1)
        module.exit_json.assert_called_with(
            changed=False,
            msg='tmp1 : {}'.format(DIR2)
        )

        # second entry
        module = self.mock_add('tmp2', DIR2)
        entries = ShellmarkEntries(path=module.params['sdirs'])
        self.assertEqual(len(entries.entries), 2)
        module.exit_json.assert_called_with(
            changed=True,
            msg='tmp2 : {}'.format(DIR2)
        )
        # third entry
        module = self.mock_add('tmp3', DIR3)
        entries = ShellmarkEntries(path=module.params['sdirs'])
        self.assertEqual(len(entries.entries), 3)
        module.exit_json.assert_called_with(
            changed=True,
            msg='tmp3 : {}'.format(DIR3)
        )

        # nonexistent
        module = self.mock_add('tmp4', '/jhkskdflsuizqwewqkfsfdlksjkui')
        entries = ShellmarkEntries(path=module.params['sdirs'])
        # TODO fix
        # module.exit_json.assert_called_with(skipped=True, msg='')

        # Check casesensitivity
        module = self.mock_add('TMP1', DIR1)
        entries = ShellmarkEntries(path=module.params['sdirs'])
        self.assertEqual(len(entries.entries), 4)
        module.exit_json.assert_called_with(
            changed=True,
            msg='TMP1 : {}'.format(DIR1)
        )

        # TODO: fix
        # module = self.mock_add('T M P 1', DIR1)
        # module.exit_json.assert_called_with(
        #     changed=True,
        #     msg='TMP1 : {}'.format(DIR1)
        # )


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

    @unittest.skip('Fix later')
    def test_delete_by_mark(self):
        module = mock_main({
            'sdirs': self.sdirs,
            'mark': 'tmp1',
            'state': 'absent'})

        entries = ShellmarkEntries(path=module.params['sdirs'])
        self.assertEqual(len(entries.entries), 2)
        module.exit_json.assert_called_with(
            changed=True,
            msg='tmp1'
        )

    @unittest.skip('Fix later')
    def test_delete_nonexistent(self):
        non_existent = '/tmp/tmp34723423643646346etfjf34gegf623646'
        module = mock_main({
            'sdirs': self.sdirs,
            'path': non_existent,
            'state': 'absent'})
        entries = ShellmarkEntries(path=module.params['sdirs'])
        self.assertEqual(len(entries.entries), 3)
        module.exit_json.assert_called_with(
            changed=False,
            msg=non_existent
        )

    def test_delete_by_path(self):
        mock_main({
            'sdirs': self.sdirs,
            'path': DIR1,
            'state': 'absent'})
        # entries = ShellmarkEntries(path=module.params['sdirs'])
        # TODO: fix
        # self.assertEqual(len(entries.entries), 2)
        # module.exit_json.assert_called_with(
        #     changed=True,
        #     msg=''
        # )

    @unittest.skip('Fix later')
    def test_delete_by_path_and_mark(self):
        module = mock_main({
            'sdirs': self.sdirs,
            'mark': 'tmp1',
            'path': DIR1,
            'state': 'absent'})
        entries = ShellmarkEntries(path=module.params['sdirs'])
        self.assertEqual(len(entries.entries), 2)
        module.exit_json.assert_called_with(
            changed=True,
            msg='tmp1 : {}'.format(DIR1)
        )

    @unittest.skip('Fix later')
    def test_delete_casesensitivity(self):
        module = mock_main({
            'sdirs': self.sdirs,
            'mark': 'TMP1',
            'state': 'absent'})
        entries = ShellmarkEntries(path=module.params['sdirs'])
        self.assertEqual(len(entries.entries), 3)
        module.exit_json.assert_called_with(
            changed=False,
            msg='TMP1'
        )


class TestFunctionWithMockCleanUp(unittest.TestCase):

    @unittest.skip('Fix later')
    def test_cleanup(self):
        path = tmp_dir()
        no = 'export DIR_tmpb="/tmpXDR34723df4WER/d4REd4RE64er64erb"\n'
        content = no + no + no + \
            'export DIR_exists="' + path + '"\n' + no + no + no
        sdirs = create_tmp_text_file_with_content(content)

        module = mock_main({
            'cleanup': True,
            'sdirs': sdirs}
        )
        entries = ShellmarkEntries(path=module.params['sdirs'])
        self.assertEqual(len(entries.entries), 1)
        self.assertEqual(entries.entries[0].path, path)

        module.exit_json.assert_called_with(
            changed=True,
            msg=''
        )


class TestClassEntry(unittest.TestCase):

    def assertNormalizePath(self, path, result):
        entry = Entry(mark='test', path=DIR1)
        entry._home_dir = '/home/jf'
        self.assertEqual(entry.normalize_path(path), result)

    def test_init_by_mark_and_path(self):
        entry = Entry(mark='test', path='/tmp')
        self.assertEqual(entry.mark, 'test')
        self.assertEqual(entry.path, '/tmp')

    def test_init_by_entry(self):
        entry = Entry(entry='export DIR_test=\"/tmp\"')
        self.assertEqual(entry.mark, 'test')
        self.assertEqual(entry.path, '/tmp')

    def test_init_path_normalization_trailing_slash(self):
        entry = Entry(mark='test', path='/tmp/')
        self.assertEqual(entry.path, '/tmp')

    @mock.patch('os.path.exists')
    def test_init_path_normalization_home_dir(self, os_path_exists):
        home_dir = pwd.getpwuid(os.getuid()).pw_dir
        entry = Entry(mark='test', path='$HOME/tmp')
        self.assertEqual(entry.mark, 'test')
        self.assertEqual(entry.path, '{}/tmp'.format(home_dir))

    def test_init_exception_all_parameters(self):
        with self.assertRaises(ValueError) as cm:
            Entry(path='p', mark='m', entry='e')
        self.assertEqual(
            str(cm.exception),
            'Specify entry OR both path and mark.'
        )

    def test_init_exception_path_and_entry(self):
        with self.assertRaises(ValueError) as cm:
            Entry(path='p', entry='e')
        self.assertEqual(
            str(cm.exception),
            'Specify entry OR both path and mark.'
        )

    def test_init_exception_mark_and_entry(self):
        with self.assertRaises(ValueError) as cm:
            Entry(mark='m', entry='e')
        self.assertEqual(
            str(cm.exception),
            'Specify entry OR both path and mark.'
        )

    def test_init_exception_disallowed_character(self):
        with self.assertRaises(MarkInvalidError) as cm:
            Entry(path='p', mark='ö')
        self.assertEqual(
            str(cm.exception),
            'Invalid mark string: “ö”. Allowed characters for bookmark names '
            'are: “0-9a-zA-Z_”.'
        )

    def test_init_exception_disallowed_character_validate_false(self):
        entry = Entry(path='p', mark='ö', validate=False)
        self.assertEqual(entry.mark, 'ö')

    def test_init_exception_path_non_existent(self):
        with self.assertRaises(NoPathError) as cm:
            Entry(path='xxx', mark='xxx')
        self.assertIn(
            'xxx” doesn’t exist.',
            str(cm.exception)
        )

    def test_init_exception_path_non_existent_validate_false(self):
        entry = Entry(path='xxx', mark='xxx', validate=False)
        self.assertEqual(entry.path, 'xxx')

    def test_method_to_export_string(self):
        entry = Entry(mark='test', path='/tmp')
        self.assertEqual(
            entry.to_export_string(),
            'export DIR_test="/tmp"'
        )

    def test_method_normalize_path(self):
        self.assertNormalizePath('/tmp/lol', '/tmp/lol')
        self.assertNormalizePath('~/.lol', '/home/jf/.lol')
        self.assertNormalizePath('', '')
        self.assertNormalizePath('/', '/')
        self.assertNormalizePath(False, '')
        self.assertNormalizePath('/tmp/', '/tmp')
        self.assertNormalizePath('$HOME/tmp', '/home/jf/tmp')

    def test_method_check_mark(self):
        self.assertEqual(Entry.check_mark('lol'), True)
        self.assertEqual(Entry.check_mark('LOL_lol_123'), True)
        self.assertEqual(Entry.check_mark('l'), True)
        self.assertEqual(Entry.check_mark('1'), True)
        self.assertEqual(Entry.check_mark('_'), True)
        self.assertEqual(Entry.check_mark('l o l'), False)
        self.assertEqual(Entry.check_mark('löl'), False)
        self.assertEqual(Entry.check_mark('l-l'), False)
        self.assertEqual(Entry.check_mark('l,l'), False)


class TestClassShellmarkEntries(unittest.TestCase):

    def test_init_existent_file(self):
        entries = ShellmarkEntries(path=os.path.join('test', 'files', 'sdirs'))
        self.assertEqual(entries.entries[0].mark, 'dir1')
        self.assertEqual(entries.entries[1].mark, 'dir2')
        self.assertEqual(entries.entries[2].mark, 'dir3')
        self.assertEqual(entries._index['marks']['dir1'], [0])
        self.assertEqual(entries._index['marks']['dir2'], [1])
        self.assertEqual(entries._index['marks']['dir3'], [2])

    def test_init_non_existent_file(self):
        entries = ShellmarkEntries(path=os.path.join('test', 'xxx'))
        self.assertEqual(len(entries.entries), 0)
        self.assertEqual(len(entries._index['marks']), 0)
        self.assertEqual(len(entries._index['paths']), 0)

    def test_property_changed(self):
        entries = ShellmarkEntries(path=os.path.join('test', 'files', 'sdirs'))
        self.assertEqual(entries.changed, False)
        entries.add_entry(mark='dir1', path=DIR1)
        self.assertEqual(entries.changed, True)

    def test_method__list_intersection(self):
        list_intersection = ShellmarkEntries._list_intersection
        self.assertEqual(list_intersection([1], [1]), [1])
        self.assertEqual(list_intersection([1], [2]), [])
        self.assertEqual(list_intersection([1, 2], [1, 2]), [1, 2])
        self.assertEqual(list_intersection([2, 1], [1, 2]), [1, 2])
        self.assertEqual(list_intersection([2, 1, 3], [1, 2]), [1, 2])
        self.assertEqual(list_intersection([2, 1, 3], []), [])

    def test_method__store_index_number(self):
        sdirs = tmp_file()
        entries = ShellmarkEntries(path=sdirs)
        entries._store_index_number('mark', 'downloads', 7)
        self.assertEqual(entries._index['marks']['downloads'], [7])

        # The same again
        entries._store_index_number('mark', 'downloads', 7)
        self.assertEqual(entries._index['marks']['downloads'], [7])

        # Add another index number.
        entries._store_index_number('mark', 'downloads', 9)
        self.assertEqual(entries._index['marks']['downloads'], [7, 9])

        # Add a lower index number.
        entries._store_index_number('mark', 'downloads', 5)
        self.assertEqual(entries._index['marks']['downloads'], [5, 7, 9])

        with self.assertRaises(ValueError) as cm:
            entries._store_index_number('lol', 'downloads', 1)
        self.assertEqual(
            str(cm.exception),
            'attribute_name “lol” unkown.'
        )

    def test_method__update_index(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark='dir1', path=DIR1)
        self.assertEqual(entries._index['marks']['dir1'], [0])
        self.assertEqual(entries._index['paths'][DIR1], [0])

        # Delete the index store.
        delattr(entries, '_index')
        with self.assertRaises(AttributeError):
            getattr(entries, '_index')

        # Regenerate index.
        entries._update_index()
        self.assertEqual(entries._index['marks']['dir1'], [0])
        self.assertEqual(entries._index['paths'][DIR1], [0])

    def test_method__get_indexes(self):
        entries = ShellmarkEntries(path=os.path.join('test', 'files', 'sdirs'))
        self.assertEqual(entries._get_indexes(mark='dir1'), [0])
        self.assertEqual(entries._get_indexes(path=DIR2), [1])
        self.assertEqual(entries._get_indexes(mark='dir3', path=DIR3), [2])

        with self.assertRaises(ValueError) as cm:
            entries._get_indexes(mark='dir1', path=DIR3)
        self.assertIn(
            'mark (dir1) and path',
            str(cm.exception)
        )

    def test_method_get_entry_by_index(self):
        entries = ShellmarkEntries(path=os.path.join('test', 'files', 'sdirs'))
        entry = entries.get_entry_by_index(0)
        self.assertEqual(entry.mark, 'dir1')
        entry = entries.get_entry_by_index(1)
        self.assertEqual(entry.mark, 'dir2')
        entry = entries.get_entry_by_index(2)
        self.assertEqual(entry.mark, 'dir3')

    def test_method_get_entries(self):
        entries = ShellmarkEntries(path=os.path.join('test', 'files', 'sdirs'))
        path = os.path.abspath(os.path.join('test', 'files', 'dir1'))

        result = entries.get_entries(mark='dir1')
        self.assertEqual(result[0].mark, 'dir1')

        result = entries.get_entries(path=path)
        self.assertEqual(result[0].mark, 'dir1')

        result = entries.get_entries(mark='dir1', path=path)
        self.assertEqual(result[0].mark, 'dir1')

        with self.assertRaises(ValueError) as cm:
            entries.get_entries(mark='dir2', path=path)
        self.assertIn(
            'mark (dir2) and path',
            str(cm.exception)
        )

        # Get an entry which doesn’t exist by mark.
        self.assertEqual(entries.get_entries(mark='lol'), [])

        # Get an entry which doesn’t exist by path.
        self.assertEqual(entries.get_entries(path='lol'), [])

    def test_method_add_entry(self):
        entries = ShellmarkEntries(path=os.path.join('test', 'xxx'))

        entries.add_entry(mark='dir1', path=DIR1)
        self.assertEqual(len(entries.entries), 1)
        self.assertEqual(entries.entries[0].mark, 'dir1')
        self.assertEqual(entries._index['marks']['dir1'], [0])

        entries.add_entry(mark='dir2', path=DIR2)
        self.assertEqual(len(entries.entries), 2)
        self.assertEqual(entries.entries[1].mark, 'dir2')
        self.assertEqual(entries._index['marks']['dir2'], [1])

    def test_method_add_entry_exception(self):
        entries = ShellmarkEntries(path=tmp_file())
        with self.assertRaises(MarkInvalidError):
            entries.add_entry(mark='dör1', path=DIR1)
        with self.assertRaises(MarkInvalidError):
            entries.add_entry(mark='d i r 1', path=DIR1)
        with self.assertRaises(MarkInvalidError):
            entries.add_entry(mark='dir 1', path=DIR1)

    def test_method_add_entry_duplicates(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark='dir1', path=DIR1)
        entries.add_entry(mark='dir1', path=DIR1)
        entries.add_entry(mark='dir1', path=DIR1)
        self.assertEqual(len(entries.entries), 3)
        self.assertEqual(entries._index['marks']['dir1'], [0, 1, 2])
        self.assertEqual(entries._index['paths'][DIR1], [0, 1, 2])

    def test_method_add_entry_avoid_duplicate_marks(self):
        entries = ShellmarkEntries(path=tmp_file())
        self.assertEqual(entries.add_entry(mark='dir1', path=DIR1), 0)
        self.assertEqual(
            entries.add_entry(mark='dir1', path=DIR1,
                              avoid_duplicate_marks=True),
            False
        )
        self.assertEqual(len(entries.entries), 1)
        self.assertEqual(
            entries.add_entry(mark='dir1', path=DIR1,
                              avoid_duplicate_marks=True,
                              delete_old_entries=True),
            0
        )
        self.assertEqual(len(entries.entries), 1)

    def test_method_add_entry_avoid_duplicate_paths(self):
        entries = ShellmarkEntries(path=tmp_file())
        self.assertEqual(entries.add_entry(mark='dir1', path=DIR1), 0)
        self.assertEqual(
            entries.add_entry(mark='dir1', path=DIR1,
                              avoid_duplicate_paths=True),
            False
        )
        self.assertEqual(len(entries.entries), 1)
        self.assertEqual(
            entries.add_entry(mark='dir1', path=DIR1,
                              avoid_duplicate_paths=True,
                              delete_old_entries=True),
            0
        )
        self.assertEqual(len(entries.entries), 1)

    def test_method_add_entry_avoid_duplicates(self):
        entries = ShellmarkEntries(path=tmp_file())
        self.assertEqual(entries.add_entry(mark='dir1', path=DIR1), 0)
        self.assertEqual(
            entries.add_entry(mark='dir1', path=DIR1,
                              avoid_duplicate_marks=True,
                              avoid_duplicate_paths=True),
            False
        )
        self.assertEqual(len(entries.entries), 1)
        self.assertEqual(
            entries.add_entry(mark='dir1', path=DIR1,
                              avoid_duplicate_marks=True,
                              avoid_duplicate_paths=True,
                              delete_old_entries=True),
            0
        )
        self.assertEqual(len(entries.entries), 1)

    def test_method_update_entries(self):
        entries = ShellmarkEntries(path=os.path.join('test', 'files', 'sdirs'))
        entries.update_entries(old_mark='dir1', new_mark='new1')
        result = entries.get_entries(mark='new1')
        self.assertEqual(result[0].path, DIR1)

    def test_method_update_entries_duplicates(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark='dir1', path=DIR1)
        entries.add_entry(mark='dir1', path=DIR1)
        entries.add_entry(mark='dir1', path=DIR1)
        entries.update_entries(old_mark='dir1', new_mark='new1')
        self.assertEqual(entries._index['marks']['new1'], [0, 1, 2])
        self.assertEqual(entries._index['paths'][DIR1], [0, 1, 2])

    def test_method_delete_entries(self):
        entries = ShellmarkEntries(path=os.path.join('test', 'files', 'sdirs'))
        entries.delete_entries(mark='dir1')
        self.assertEqual(len(entries.entries), 2)
        entries.delete_entries(path=DIR2)
        self.assertEqual(len(entries.entries), 1)
        entries.delete_entries(mark='dir3', path=DIR3)
        self.assertEqual(len(entries.entries), 0)

        # Delete entries which don’t exist by mark.
        self.assertEqual(entries.delete_entries(mark='lol'), False)

        # Delete entries which don’t exist by path.
        self.assertEqual(entries.delete_entries(path='lol'), False)

    def test_method_delete_entries_duplicates(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark='dir1', path=DIR1)
        entries.add_entry(mark='dir1', path=DIR1)
        entries.add_entry(mark='dir1', path=DIR1)
        self.assertEqual(len(entries.entries), 3)
        entries.delete_entries(mark='dir1')
        self.assertEqual(len(entries.entries), 0)

    def test_method_delete_duplicates(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark='mark', path=DIR1)
        entries.add_entry(mark='mark', path=DIR2)
        entries.add_entry(mark='other', path=DIR2)
        entries.delete_duplicates(marks=True, paths=False)
        self.assertEqual(entries.entries[0].path, DIR2)
        self.assertEqual(entries.entries[1].path, DIR2)

        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark='mark1', path=DIR1)
        entries.add_entry(mark='mark2', path=DIR1)
        entries.add_entry(mark='mark2', path=DIR2)
        entries.delete_duplicates(marks=False, paths=True)
        self.assertEqual(entries.entries[0].mark, 'mark2')
        self.assertEqual(entries.entries[1].mark, 'mark2')

        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark='mark1', path=DIR1)
        entries.add_entry(mark='mark1', path=DIR1)
        entries.add_entry(mark='mark2', path=DIR1)
        entries.add_entry(mark='mark1', path=DIR2)
        entries.delete_duplicates(marks=True, paths=True)
        self.assertEqual(len(entries.entries), 2)
        self.assertEqual(entries.entries[0].mark, 'mark2')
        self.assertEqual(entries.entries[0].path, DIR1)
        self.assertEqual(entries.entries[1].mark, 'mark1')
        self.assertEqual(entries.entries[1].path, DIR2)

    def test_method_sort(self):
        sdirs = tmp_file()
        entries = ShellmarkEntries(path=sdirs)
        entries.add_entry(mark='dir3', path=DIR1)
        entries.add_entry(mark='dir2', path=DIR2)
        entries.add_entry(mark='dir1', path=DIR3)
        self.assertEqual(entries.entries[0].mark, 'dir3')
        self.assertEqual(entries.entries[1].mark, 'dir2')
        self.assertEqual(entries.entries[2].mark, 'dir1')
        self.assertEqual(entries.entries[0].path, DIR1)
        self.assertEqual(entries.entries[1].path, DIR2)
        self.assertEqual(entries.entries[2].path, DIR3)

        entries.sort()
        self.assertEqual(entries.entries[0].mark, 'dir1')
        self.assertEqual(entries.entries[1].mark, 'dir2')
        self.assertEqual(entries.entries[2].mark, 'dir3')

        entries.sort(reverse=True)
        self.assertEqual(entries.entries[0].mark, 'dir3')
        self.assertEqual(entries.entries[1].mark, 'dir2')
        self.assertEqual(entries.entries[2].mark, 'dir1')

        entries.sort(attribute_name='path')
        self.assertEqual(entries.entries[0].path, DIR1)
        self.assertEqual(entries.entries[1].path, DIR2)
        self.assertEqual(entries.entries[2].path, DIR3)

        entries.sort(attribute_name='path', reverse=True)
        self.assertEqual(entries.entries[0].path, DIR3)
        self.assertEqual(entries.entries[1].path, DIR2)
        self.assertEqual(entries.entries[2].path, DIR1)

    def test_method_write(self):
        old_path = os.path.join('test', 'files', 'sdirs')
        entries = ShellmarkEntries(path=old_path)
        new_path = tempfile.mkstemp()[1]
        entries.write(new_path=new_path)
        new_path_content = open(new_path, 'r').read()
        self.assertTrue(new_path_content)

    def test_combinations(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark='dir1', path=DIR1)
        entries.add_entry(mark='dir2', path=DIR2)
        entries.add_entry(mark='dir3', path=DIR3)
        self.assertEqual(entries.get_entries(mark='dir3')[0].path, DIR3)

        # Delete one entry
        entries.delete_entries(mark='dir2')
        self.assertEqual(entries.get_entries(mark='dir3')[0].path, DIR3)

        # Sort
        entries.sort(reverse=True)
        self.assertEqual(entries.get_entries(mark='dir3')[0].path, DIR3)

        # Update one entry
        entries.update_entries(old_mark='dir1', new_path=DIR2)
        self.assertEqual(entries.get_entries(mark='dir3')[0].path, DIR3)

        entries.write()

        content = entries.get_raw()
        self.assertEqual(
            content,
            'export DIR_dir3="{0}/dir3"\nexport DIR_dir1="{0}/dir2"\n'
            .format(TEST_PATH)
        )

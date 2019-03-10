# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division)
from ansible.compat.tests import unittest
# import unittest
import mock
import shellmarks
from shellmarks import Entry, ShellmarkEntries
import tempfile
import pwd
import os
__metaclass__ = type


def sdirs_by_content(content):
    sdirs = tmp_file()
    f = open(sdirs, 'w')
    f.write(content)
    f.close()
    return sdirs


def tmp_file():
    return tempfile.mkstemp()[1]


def tmp_dir():
    return tempfile.mkdtemp()


def read(sdirs):
    return open(sdirs, 'r').readlines()


test_files = os.path.abspath(os.path.join('test', 'files'))
dir1 = os.path.join(test_files, 'dir1')
dir2 = os.path.join(test_files, 'dir2')
dir3 = os.path.join(test_files, 'dir3')


class TestUnitTest(unittest.TestCase):

    def test_shellmarks(self):
        sm = shellmarks.ShellMarks({'mark': 'lol', 'path': '/lol'})
        self.assertEqual('export DIR_lol="/lol"\n', sm.generate_entry())
        self.assertFalse(sm.error)

    def test_forbidden(self):
        sm = shellmarks.ShellMarks({'mark': 'l-l', 'path': '/lol'})
        self.assertTrue(sm.error)
        sm = shellmarks.ShellMarks({'mark': 'l l', 'path': '/lol'})
        self.assertTrue(sm.error)
        sm = shellmarks.ShellMarks({'mark': 'löl', 'path': '/lol'})
        self.assertTrue(sm.error)
        sm = shellmarks.ShellMarks({'mark': 'l,l', 'path': '/lol'})
        self.assertTrue(sm.error)


class TestFunction(unittest.TestCase):

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


class TestObject(unittest.TestCase):

    def test_present(self):
        sdirs = tmp_file()
        shellmarks.ShellMarks({'sdirs': sdirs, 'path': '/tmp',
                               'mark': 'tmp'})

        self.assertEqual(read(sdirs)[0], 'export DIR_tmp="/tmp"\n')

    def test_sort(self):
        content = 'export DIR_tmpb="/tmp/b"\n' + \
            'export DIR_tmpc="/tmp/c"\n' + \
            'export DIR_tmpa="/tmp/a"\n'
        sdirs = sdirs_by_content(content)

        sm = shellmarks.ShellMarks({'sorted': False, 'sdirs': sdirs}, True)
        self.assertEqual(sm.entries[0], 'export DIR_tmpb="/tmp/b"\n')

        sm = shellmarks.ShellMarks({'sorted': True, 'sdirs': sdirs}, True)
        self.assertEqual(sm.entries[0], 'export DIR_tmpa="/tmp/a"\n')


class TestAdd(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.sdirs = tmp_file()
        self.dir1 = tmp_dir()
        self.dir2 = tmp_dir()
        self.dir3 = tmp_dir()

    def addShellMarks(self, mark, path):
        sm = shellmarks.ShellMarks({'sdirs': self.sdirs, 'path': path,
                                    'mark': mark})
        return sm

    def test_add(self):
        sm = self.addShellMarks('tmp1', self.dir1)
        self.assertEqual(len(sm.entries), 1)
        self.assertEqual(sm.skipped, False)
        self.assertEqual(sm.changed, True)

        # same entry
        sm = self.addShellMarks('tmp1', self.dir1)
        self.assertEqual(len(sm.entries), 1)
        self.assertEqual(sm.changed, False)

        # same mark
        sm = self.addShellMarks('tmp1', self.dir2)
        self.assertEqual(len(sm.entries), 1)
        self.assertEqual(sm.changed, False)

        # second entry
        sm = self.addShellMarks('tmp2', self.dir2)
        self.assertEqual(len(sm.entries), 2)
        self.assertEqual(sm.skipped, False)
        self.assertEqual(sm.changed, True)

        # third entry
        sm = self.addShellMarks('tmp3', self.dir3)
        self.assertEqual(len(sm.entries), 3)
        self.assertEqual(sm.skipped, False)
        self.assertEqual(sm.changed, True)

        # nonexistent
        sm = self.addShellMarks('tmp4', '/jhkskdflsuizqwewqkfsfdlksjkui')
        self.assertEqual(sm.skipped, True)
        self.assertEqual(sm.changed, False)

        # Check casesensitivity
        sm = self.addShellMarks('TMP1', self.dir1)
        self.assertEqual(len(sm.entries), 4)
        self.assertEqual(sm.changed, True)


class TestDel(unittest.TestCase):

    def addShellMarks(self, mark, path):
        return shellmarks.ShellMarks({'sdirs': self.sdirs, 'path': path,
                                      'mark': mark})

    def setUp(self):
        self.sdirs = tmp_file()
        self.dir1 = tmp_dir()
        self.dir2 = tmp_dir()
        self.dir3 = tmp_dir()

        self.addShellMarks('tmp1', self.dir1)
        self.addShellMarks('tmp2', self.dir2)
        self.addShellMarks('tmp3', self.dir3)

    def test_delete_by_mark(self):
        sm = shellmarks.ShellMarks({
            'sdirs': self.sdirs,
            'mark': 'tmp1',
            'state': 'absent'})
        self.assertEqual(len(sm.entries), 2)
        self.assertEqual(sm.skipped, False)
        self.assertEqual(sm.changed, True)

        for entry in sm.entries:
            if 'DIR_tmp1=' in entry:
                self.fail('Path was not deleted.')

    def test_delete_nonexistent(self):
        sm = shellmarks.ShellMarks({
            'sdirs': self.sdirs,
            'path': '/tmp/tmp34723423643646346etfjf34gegf623646',
            'state': 'absent'})
        self.assertEqual(len(sm.entries), 3)
        self.assertEqual(sm.skipped, False)
        self.assertEqual(sm.changed, False)

    def test_delete_by_path(self):
        sm = shellmarks.ShellMarks({
            'sdirs': self.sdirs,
            'path': self.dir1,
            'state': 'absent'})
        self.assertEqual(len(sm.entries), 2)
        self.assertEqual(sm.skipped, False)
        self.assertEqual(sm.changed, True)

        for entry in sm.entries:
            if self.dir1 in entry:
                self.fail('Path was not deleted.')

    def test_delete_by_path_and_mark(self):
        sm = shellmarks.ShellMarks({
            'sdirs': self.sdirs,
            'mark': 'tmp1',
            'path': self.dir1,
            'state': 'absent'})
        self.assertEqual(len(sm.entries), 2)
        self.assertEqual(sm.skipped, False)
        self.assertEqual(sm.changed, True)

        for entry in sm.entries:
            if self.dir1 in entry:
                self.fail('Path was not deleted.')

    def test_delete_casesensitivity(self):
        sm = shellmarks.ShellMarks({
            'sdirs': self.sdirs,
            'mark': 'TMP1',
            'state': 'absent'})
        self.assertEqual(len(sm.entries), 3)
        self.assertEqual(sm.skipped, False)
        self.assertEqual(sm.changed, False)


class TestCleanUp(unittest.TestCase):

    def test_cleanup(self):
        path = tmp_dir()
        no = 'export DIR_tmpb="/tmpXDR34723df4WER/d4REd4RE64er64erb"\n'
        content = no + no + no + \
            'export DIR_exists="' + path + '"\n' + no + no + no
        sdirs = sdirs_by_content(content)

        sm = shellmarks.ShellMarks({
            'cleanup': True,
            'sdirs': sdirs})

        self.assertEqual(sm.changed, True)
        self.assertEqual(sm.skipped, False)
        self.assertEqual(len(sm.entries), 1)
        self.assertEqual(shellmarks.get_path(sm.entries[0]), path)


class TestFunctions(unittest.TestCase):

    entry = 'export DIR_tmp="/tmp"'

    def assertNormalizePath(self, path, home_dir, result):
        self.assertEqual(shellmarks.normalize_path(path, home_dir), result)

    def test_get_path(self):
        self.assertEqual(shellmarks.get_path(self.entry), '/tmp')

    def test_get_mark(self):
        self.assertEqual(shellmarks.get_mark(self.entry), 'tmp')

    def test_del_entries(self):
        entries = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
        shellmarks.del_entries(entries, [1, 5, 11])

        self.assertEqual(entries[1], 'c')
        self.assertEqual(entries[5], 'h')
        self.assertEqual(entries[8], 'k')

    def test_normalize_path(self):
        self.assertNormalizePath('/tmp/lol', '/home/jf', '/tmp/lol')
        self.assertNormalizePath('~/.lol', '/home/jf', '/home/jf/.lol')
        self.assertNormalizePath('', '/home/jf', '')
        # self.assertNormalizePath('/', '/home/jf', '/')
        self.assertNormalizePath(False, '/home/jf', '')
        self.assertNormalizePath('/tmp/', '/home/jf', '/tmp')
        self.assertNormalizePath('$HOME/tmp', '/home/jf', '/home/jf/tmp')

    def test_check_mark(self):
        self.assertEqual(shellmarks.check_mark('lol'), True)
        self.assertEqual(shellmarks.check_mark('LOL_lol_123'), True)
        self.assertEqual(shellmarks.check_mark('l'), True)
        self.assertEqual(shellmarks.check_mark('1'), True)
        self.assertEqual(shellmarks.check_mark('_'), True)
        self.assertEqual(shellmarks.check_mark('l o l'), False)
        self.assertEqual(shellmarks.check_mark('löl'), False)
        self.assertEqual(shellmarks.check_mark('l-l'), False)
        self.assertEqual(shellmarks.check_mark('l,l'), False)


class TestClassEntry(unittest.TestCase):

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
        with self.assertRaises(ValueError) as cm:
            Entry(path='p', mark='ö')
        self.assertEqual(
            str(cm.exception),
            'Allowed characters for mark: 0-9a-zA-Z_'
        )

    def test_init_exception_path_non_existent(self):
        with self.assertRaises(ValueError) as cm:
            Entry(path='xxx', mark='xxx')
        self.assertIn(
            'xxx” doesn’t exist.',
            str(cm.exception)
        )

    def test_method_to_entry_string(self):
        entry = Entry(mark='test', path='/tmp')
        self.assertEqual(
            entry.to_export_string(),
            'export DIR_test="/tmp"'
        )


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
        entries.add_entry(mark='dir1', path=dir1)
        self.assertEqual(entries._index['marks']['dir1'], [0])
        self.assertEqual(entries._index['paths'][dir1], [0])

        # Delete the index store.
        delattr(entries, '_index')
        with self.assertRaises(AttributeError):
            getattr(entries, '_index')

        # Regenerate index.
        entries._update_index()
        self.assertEqual(entries._index['marks']['dir1'], [0])
        self.assertEqual(entries._index['paths'][dir1], [0])

    def test_method__get_indexes(self):
        entries = ShellmarkEntries(path=os.path.join('test', 'files', 'sdirs'))
        self.assertEqual(entries._get_indexes(mark='dir1'), [0])
        self.assertEqual(entries._get_indexes(path=dir2), [1])
        self.assertEqual(entries._get_indexes(mark='dir3', path=dir3), [2])

        with self.assertRaises(ValueError) as cm:
            entries._get_indexes(mark='dir1', path=dir3)
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

    def test_method_add_entry(self):
        entries = ShellmarkEntries(path=os.path.join('test', 'xxx'))

        entries.add_entry(mark='dir1', path=dir1)
        self.assertEqual(len(entries.entries), 1)
        self.assertEqual(entries.entries[0].mark, 'dir1')
        self.assertEqual(entries._index['marks']['dir1'], [0])

        entries.add_entry(mark='dir2', path=dir2)
        self.assertEqual(len(entries.entries), 2)
        self.assertEqual(entries.entries[1].mark, 'dir2')
        self.assertEqual(entries._index['marks']['dir2'], [1])

    def test_method_add_entry_exception(self):
        entries = ShellmarkEntries(path=tmp_file())
        with self.assertRaises(ValueError):
            entries.add_entry(mark='dör1', path=dir1)
        with self.assertRaises(ValueError):
            entries.add_entry(mark='d i r 1', path=dir1)
        with self.assertRaises(ValueError):
            entries.add_entry(mark='dir 1', path=dir1)

    def test_method_add_entry_duplicates(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark='dir1', path=dir1)
        entries.add_entry(mark='dir1', path=dir1)
        entries.add_entry(mark='dir1', path=dir1)
        self.assertEqual(len(entries.entries), 3)
        self.assertEqual(entries._index['marks']['dir1'], [0, 1, 2])
        self.assertEqual(entries._index['paths'][dir1], [0, 1, 2])

    def test_method_update_entries(self):
        entries = ShellmarkEntries(path=os.path.join('test', 'files', 'sdirs'))
        entries.update_entries(old_mark='dir1', new_mark='new1')
        result = entries.get_entries(mark='new1')
        self.assertEqual(result[0].path, dir1)

    def test_method_update_entries_duplicates(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark='dir1', path=dir1)
        entries.add_entry(mark='dir1', path=dir1)
        entries.add_entry(mark='dir1', path=dir1)
        entries.update_entries(old_mark='dir1', new_mark='new1')
        self.assertEqual(entries._index['marks']['new1'], [0, 1, 2])
        self.assertEqual(entries._index['paths'][dir1], [0, 1, 2])

    def test_method_delete_entries(self):
        entries = ShellmarkEntries(path=os.path.join('test', 'files', 'sdirs'))
        entries.delete_entries(mark='dir1')
        self.assertEqual(len(entries.entries), 2)
        entries.delete_entries(path=dir2)
        self.assertEqual(len(entries.entries), 1)
        entries.delete_entries(mark='dir3', path=dir3)
        self.assertEqual(len(entries.entries), 0)

    def test_method_delete_entries_duplicates(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark='dir1', path=dir1)
        entries.add_entry(mark='dir1', path=dir1)
        entries.add_entry(mark='dir1', path=dir1)
        self.assertEqual(len(entries.entries), 3)
        entries.delete_entries(mark='dir1')
        self.assertEqual(len(entries.entries), 0)

    def test_method_sort(self):
        sdirs = tmp_file()
        entries = ShellmarkEntries(path=sdirs)
        entries.add_entry(mark='dir3', path=dir1)
        entries.add_entry(mark='dir2', path=dir2)
        entries.add_entry(mark='dir1', path=dir3)
        self.assertEqual(entries.entries[0].mark, 'dir3')
        self.assertEqual(entries.entries[1].mark, 'dir2')
        self.assertEqual(entries.entries[2].mark, 'dir1')
        self.assertEqual(entries.entries[0].path, dir1)
        self.assertEqual(entries.entries[1].path, dir2)
        self.assertEqual(entries.entries[2].path, dir3)

        entries.sort()
        self.assertEqual(entries.entries[0].mark, 'dir1')
        self.assertEqual(entries.entries[1].mark, 'dir2')
        self.assertEqual(entries.entries[2].mark, 'dir3')

        entries.sort(reverse=True)
        self.assertEqual(entries.entries[0].mark, 'dir3')
        self.assertEqual(entries.entries[1].mark, 'dir2')
        self.assertEqual(entries.entries[2].mark, 'dir1')

        entries.sort(attribute_name='path')
        self.assertEqual(entries.entries[0].path, dir1)
        self.assertEqual(entries.entries[1].path, dir2)
        self.assertEqual(entries.entries[2].path, dir3)

        entries.sort(attribute_name='path', reverse=True)
        self.assertEqual(entries.entries[0].path, dir3)
        self.assertEqual(entries.entries[1].path, dir2)
        self.assertEqual(entries.entries[2].path, dir1)

    def test_method_write(self):
        old_path = os.path.join('test', 'files', 'sdirs')
        entries = ShellmarkEntries(path=old_path)
        new_path = tempfile.mkstemp()[1]
        entries.write(new_path=new_path)
        new_path_content = open(new_path, 'r').read()
        self.assertTrue(new_path_content)

# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division)
from ansible.compat.tests import unittest
# import unittest
import mock
import shellmarks
import tempfile
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


class TestUnitTest(unittest.TestCase):

    def test_shellmarks(self):
        sm = shellmarks.ShellMarks({'mark': 'lol', 'path': '/lol'})
        self.assertEqual('export DIR_lol="/lol"\n', sm.generateEntry())
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

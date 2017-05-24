from __future__ import (absolute_import, division)
from ansible.compat.tests import unittest
# import unittest
import mock
import shellmarks
import tempfile
__metaclass__ = type


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

    def test_forbidden_char_dash(self):
        sm = shellmarks.ShellMarks({'mark': 'l-l', 'path': '/lol'})
        self.assertEqual('export DIR_ll="/lol"\n', sm.generateEntry())


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
            mark=dict(required=True, aliases=['bookmark']),
            path=dict(required=True, aliases=['src']),
            replace_home=dict(default=True, type='bool'),
            sdirs=dict(default='~/.sdirs'),
            sorted=dict(default=True, type='bool'),
            state=dict(default='present', choices=['present', 'absent']),
        )

        assert(mock.call(argument_spec=expected,
               supports_check_mode=True) == AnsibleModule.call_args)

        lines = read(sdirs)
        self.assertEqual(lines[0], 'export DIR_tmp="/tmp"\n')


class TestObject(unittest.TestCase):

    def test_present(self):
        sdirs = tmp_file()
        sm = shellmarks.ShellMarks({'sdirs': sdirs, 'path': '/tmp',
                                    'mark': 'tmp'})

        self.assertEqual(read(sdirs)[0], 'export DIR_tmp="/tmp"\n')

    def test_add(self):
        pass

    def test_sort(self):
        sdirs = tmp_file()
        content = 'export DIR_tmpb="/tmp/b"\n' + \
            'export DIR_tmpc="/tmp/c"\n' + \
            'export DIR_tmpa="/tmp/a"\n'

        f = open(sdirs, 'w')
        f.write(content)
        f.close()

        sm = shellmarks.ShellMarks({'sorted': True, 'sdirs': sdirs})


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


class TestDel(unittest.TestCase):

    def addShellMarks(self, mark, path):
        sm = shellmarks.ShellMarks({'sdirs': self.sdirs, 'path': path,
                                    'mark': mark})
        return sm

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

    def test_delete_nonexistent(self):
        sm = shellmarks.ShellMarks({
            'sdirs': self.sdirs,
            'path': '/tmp/tmp34723423643646346etfjf34gegf623646',
            'state': 'absent'})
        self.assertEqual(len(sm.entries), 3)
        self.assertEqual(sm.skipped, False)
        self.assertEqual(sm.changed, False)

    def test_delete_py_path(self):
        sm = shellmarks.ShellMarks({
            'sdirs': self.sdirs,
            'path': self.dir1,
            'state': 'absent'})
        self.assertEqual(len(sm.entries), 2)
        self.assertEqual(sm.skipped, False)
        self.assertEqual(sm.changed, True)

    def test_delete_py_path(self):
        sm = shellmarks.ShellMarks({
            'sdirs': self.sdirs,
            'mark': 'tmp1',
            'path': self.dir1,
            'state': 'absent'})
        self.assertEqual(len(sm.entries), 2)
        self.assertEqual(sm.skipped, False)
        self.assertEqual(sm.changed, True)

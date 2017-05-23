from __future__ import (absolute_import, division)
from ansible.compat.tests import unittest
#import unittest
import mock
import shellmarks
import tempfile
__metaclass__ = type


def tmp():
    return tempfile.mkstemp()[1]

def read(sdirs):
    return open(sdirs, 'r').readlines()

class TestUnitTest(unittest.TestCase):

    def test_shellmarks(self):
        m = shellmarks.mark_entry
        entry = m('lol', '/lol')
        self.assertEqual('export DIR_lol="/lol"\n', entry)
        sm = shellmarks.ShellMarks({'mark': 'lol', 'path': '/lol'})
        self.assertEqual('export DIR_lol="/lol"\n', sm.generateEntry())

    def test_forbidden_char_dash(self):
        m = shellmarks.mark_entry
        entry = m('l-l', '/lol')
        self.assertEqual('export DIR_ll="/lol"\n', entry)
        sm = shellmarks.ShellMarks({'mark': 'l-l', 'path': '/lol'})
        self.assertEqual('export DIR_ll="/lol"\n', sm.generateEntry())

class TestFunction(unittest.TestCase):

    @mock.patch("shellmarks.AnsibleModule")
    def test_mock(self, AnsibleModule):
        sdirs = tmp()
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
        sdirs = tmp()
        sm = shellmarks.ShellMarks({'sdirs': sdirs, 'path': '/tmp', 'mark': 'tmp'})
        sm.process()

        self.assertEqual(read(sdirs)[0], 'export DIR_tmp="/tmp"\n')

    def test_sort(self):
        sdirs = tmp()
        content = 'export DIR_tmpb="/tmp/b"\n' + \
            'export DIR_tmpc="/tmp/c"\n' + \
            'export DIR_tmpa="/tmp/a"\n'

        f = open(sdirs, 'w')
        f.write(content)
        f.close()

        sm = shellmarks.ShellMarks({'sorted': True, 'sdirs': sdirs})
        sm.process()
        #self.assertEqual(sm.lines, 'lol')

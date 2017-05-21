from __future__ import (absolute_import, division)
from ansible.compat.tests import unittest
import mock
import shellmarks
__metaclass__ = type


class TestUnitTest(unittest.TestCase):

    def test_shellmarks(self):
        m = shellmarks.mark_entry
        entry = m('lol', '/lol')
        self.assertEqual('export DIR_lol="/lol"\n', entry)

    def test_forbidden_char_dash(self):
        m = shellmarks.mark_entry
        entry = m('l-l', '/lol')
        self.assertEqual('export DIR_ll="/lol"\n', entry)


class TestFunction(unittest.TestCase):

    @mock.patch("shellmarks.AnsibleModule")
    def test__main__success(self, AnsibleModule):
        module = AnsibleModule.return_value
        module.params = {
            "state": "present",
            "path": "/tmp",
            "mark": "tmp"
        }
        module.check_mode = False
        shellmarks.main()

        expected = dict(
            path=dict(required=True, aliases=['src']),
            state=dict(default='present', choices=['present', 'absent']),
            mark=dict(required=True, aliases=['bookmark']),
        )

        assert(mock.call(argument_spec=expected,
               supports_check_mode=True) == AnsibleModule.call_args)

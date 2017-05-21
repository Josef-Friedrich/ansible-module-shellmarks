
# First install requirements

# pip install -r test/utils/tox/requirements.txt
# Make coding more python3-ish
from __future__ import (absolute_import, division)
__metaclass__ = type

from ansible.compat.tests import unittest
# from ansible.compat.tests.mock import call, create_autospec, patch
# from ansible.module_utils.basic import AnsibleModule

import mock
import shellmarks





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
    def test__main__success(self, ansible_mod_cls):
        mod_obj = ansible_mod_cls.return_value
        args = {
            "state": "present",
            "path": "/tmp",
            "mark": "tmp"
        }
        mod_obj.params = args
        mod_obj.check_mode = False
        shellmarks.main()

        expected_arguments_spec = dict(
            path=dict(required=True, aliases=['src']),
            state=dict(default='present', choices=['present', 'absent']),
            mark=dict(required=True, aliases=['bookmark']),
        )

        assert(mock.call(argument_spec=expected_arguments_spec, supports_check_mode=True) ==
               ansible_mod_cls.call_args)



        #self.assertEqual(1, call(mod.params))


        # Exercise
# #        firstmod.save_data(mod)
#
#         # Verify
# #
#         expected = call(mod.params["url"])
#         self.assertEqual(expected, fetch.call_args)
#
#         self.assertEqual(1, write.call_count)
#         expected = call(fetch.return_value, mod.params["dest"])
#         self.assertEqual(expected, write.call_args)
#
#         self.assertEqual(1, mod.exit_json.call_count)
#         expected = call(msg="Data saved", changed=True)
#         self.assertEqual(expected, mod.exit_json.call_args)

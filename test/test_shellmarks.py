
# First install requirements

# pip install -r test/utils/tox/requirements.txt
# Make coding more python3-ish
from __future__ import (absolute_import, division)
__metaclass__ = type

from ansible.compat.tests import unittest
from ansible.compat.tests.mock import call, create_autospec, patch
from ansible.module_utils.basic import AnsibleModule

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



class TestUnitTest(unittest.TestCase):

    def test_functional(self):
        mod_cls = create_autospec(AnsibleModule)
        mod = mod_cls.return_value
        mod.params = dict(
            path="/home/jf",
            mark="home"
        )


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

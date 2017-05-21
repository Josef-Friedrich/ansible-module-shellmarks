
# First install requirements

# pip install -r test/utils/tox/requirements.txt
# Make coding more python3-ish
from __future__ import (absolute_import, division)
__metaclass__ = type

from ansible.compat.tests import unittest
from ansible.compat.tests.mock import call, create_autospec, patch
from ansible.module_utils.basic import AnsibleModule

import shellmarks


class TestShellMarks(unittest.TestCase):


    def test_shellmarks(self):
        m = shellmarks.mark_entry
        entry = m('lol', '/lol')
        self.assertEqual('export DIR_lol="/lol"\n', entry)

        entry = m('l-l', '/lol')
        self.assertEqual('export DIR_ll="/lol"\n', entry)

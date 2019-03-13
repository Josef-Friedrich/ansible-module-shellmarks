import os
import subprocess
from ansible.compat.tests import unittest


old_env = os.getenv('ANSIBLE_LIBRARY')

if old_env:
    os.putenv('ANSIBLE_LIBRARY', old_env + ':' + os.getcwd())
else:
    os.putenv('ANSIBLE_LIBRARY', os.getcwd())


class TestFunctionalWithSubprocess(unittest.TestCase):

    def test_ansible_doc(self):
        output = subprocess.check_output(['ansible-doc', 'shellmarks'])
        output = output.decode('utf-8')
        self.assertIn(
            'commonly used directories',
            output
        )


    def test_ansible_playbook(self):
        output = subprocess.run(['ansible-playbook', 'playbook.yml'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(
            'commonly used directories',
            output.stderr
        )

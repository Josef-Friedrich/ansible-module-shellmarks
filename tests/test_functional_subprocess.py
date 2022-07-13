# -*- coding: utf-8 -*-
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

    @unittest.skip('Figure out ansible-playbook in tox environment?')
    def test_ansible_playbook(self):
        output = subprocess.run([
            'ansible-playbook', '-l', 'localhost,', '-c', 'local',
            os.path.join(os.getcwd(), 'play.yml')],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding='utf-8', shell=True)
        self.assertIn(
            'Add a shellmark for the home folder',
            output.stdout
        )

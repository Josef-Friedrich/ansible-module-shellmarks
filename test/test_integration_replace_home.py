# -*- coding: utf-8 -*-
from ansible.compat.tests import unittest

from _helper import \
    create_sdirs, \
    DIR1, \
    HOME_DIR, \
    mock_main, \
    read


class TestReplaceHome(unittest.TestCase):

    @staticmethod
    def create_sdirs_file():
        entries = create_sdirs([
            ['home', HOME_DIR]
        ])
        return entries.path

    def test_replace_home_true_check_mode_false(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(params={'replace_home': True, 'sdirs': sdirs},
                                 check_mode=False)

        lines = read(sdirs)
        self.assertIn('$HOME', lines[0])
        mock_objects['module'].exit_json.assert_called_with(
            changed=True
        )

    def test_replace_home_true_state_present_check_mode_false(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(
            params={
                'replace_home': True,
                'sdirs': sdirs,
                'path': DIR1,
                'mark': 'dir1',
            },
            check_mode=False
        )

        lines = read(sdirs)
        self.assertIn('$HOME', lines[0])
        mock_objects['module'].exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    'action': 'add',
                    'mark': 'dir1',
                    'path': DIR1,
                },
            ]
        )

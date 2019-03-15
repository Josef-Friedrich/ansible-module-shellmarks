# -*- coding: utf-8 -*-
from ansible.compat.tests import unittest

from _helper import \
    create_sdirs, \
    DIR1, \
    DIR2, \
    DIR3, \
    mock_main


class TestSortTrue(unittest.TestCase):

    @staticmethod
    def create_sdirs_file():
        entries = create_sdirs([
            ['dirB', DIR2],
            ['dirC', DIR3],
            ['dirA', DIR1],
        ])
        return entries.path

    def test_sorted_true_check_mode_true(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(params={'sorted': True, 'sdirs': sdirs},
                                 check_mode=True)
        self.assertEqual(mock_objects['entries'].entries[0].mark, 'dirB')
        mock_objects['module'].exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    'action': 'sort',
                    'sort_by': 'mark',
                    'reverse': False,
                },
            ]
        )

    def test_sorted_true_check_mode_false(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(params={'sorted': True, 'sdirs': sdirs},
                                 check_mode=False)
        self.assertEqual(mock_objects['entries'].entries[0].mark, 'dirA')
        self.assertEqual(mock_objects['entries'].entries[1].mark, 'dirB')
        self.assertEqual(mock_objects['entries'].entries[2].mark, 'dirC')
        self.assertEqual(mock_objects['entries'].entries[2].mark, 'dirC')
        mock_objects['module'].exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    'action': 'sort',
                    'sort_by': 'mark',
                    'reverse': False,
                },
            ]
        )

    def test_sorted_false_check_mode_true(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(params={'sorted': False, 'sdirs': sdirs},
                                 check_mode=True)
        self.assertEqual(mock_objects['entries'].entries[0].mark, 'dirB')
        self.assertEqual(mock_objects['entries'].entries[1].mark, 'dirC')
        self.assertEqual(mock_objects['entries'].entries[2].mark, 'dirA')
        mock_objects['module'].exit_json.assert_called_with(
            changed=False
        )

    def test_sorted_false_check_mode_false(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(params={'sorted': False, 'sdirs': sdirs},
                                 check_mode=False)
        self.assertEqual(mock_objects['entries'].entries[0].mark, 'dirB')
        self.assertEqual(mock_objects['entries'].entries[1].mark, 'dirC')
        self.assertEqual(mock_objects['entries'].entries[2].mark, 'dirA')
        mock_objects['module'].exit_json.assert_called_with(
            changed=False
        )

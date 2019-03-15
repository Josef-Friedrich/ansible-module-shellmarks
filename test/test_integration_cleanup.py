# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division)
from ansible.compat.tests import unittest
from shellmarks import ShellmarkEntries


from _helper import \
    create_tmp_text_file_with_content, \
    DIR1, \
    DIR2, \
    DIR3, \
    mock_main, \
    tmp_dir, \
    tmp_file


class TestCleanup(unittest.TestCase):

    def test_cleanup(self):
        path = tmp_dir()
        no = 'export DIR_tmpb="/tmpXDR34723df4WER/d4REd4RE64er64erb"\n'
        content = no + no + no + \
            'export DIR_exists="' + path + '"\n' + no + no + no
        sdirs = create_tmp_text_file_with_content(content)

        mock_objects = mock_main({
            'cleanup': True,
            'sdirs': sdirs
        })
        self.assertEqual(len(mock_objects['entries'].entries), 1)
        self.assertEqual(mock_objects['entries'].entries[0].path, path)

        mock_objects['module'].exit_json.assert_called_with(
            changed=True,
            changes=[{'action': 'cleanup', 'count': 6}]
        )

    def test_nothing_to_do(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark='dir1', path=DIR1)
        entries.add_entry(mark='dir2', path=DIR2)
        entries.add_entry(mark='dir3', path=DIR3)
        entries.write()

        mock_objects = mock_main({
            'cleanup': True,
            'sdirs': entries.path
        })

        entries = ShellmarkEntries(path=mock_objects['module'].params['sdirs'])
        self.assertEqual(len(mock_objects['entries'].entries), 3)
        self.assertEqual(mock_objects['entries'].entries[0].path, DIR1)

        mock_objects['module'].exit_json.assert_called_with(
            changed=False
        )

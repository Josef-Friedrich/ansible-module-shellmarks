# -*- coding: utf-8 -*-
import mock
from ansible.compat.tests import unittest
from shellmarks import Entry, MarkInvalidError, NoPathError
from _helper import DIR1, HOME_DIR


class TestClassEntry(unittest.TestCase):

    def assertNormalizePath(self, path, result):
        entry = Entry(mark='test', path=DIR1)
        self.assertEqual(entry.normalize_path(path, '/home/jf'), result)

    def test_init_by_mark_and_path(self):
        entry = Entry(mark='test', path='/tmp')
        self.assertEqual(entry.mark, 'test')
        self.assertEqual(entry.path, '/tmp')

    def test_init_by_entry(self):
        entry = Entry(entry='export DIR_test=\"/tmp\"')
        self.assertEqual(entry.mark, 'test')
        self.assertEqual(entry.path, '/tmp')

    def test_init_path_normalization_trailing_slash(self):
        entry = Entry(mark='test', path='/tmp/')
        self.assertEqual(entry.path, '/tmp')

    @mock.patch('os.path.exists')
    def test_init_path_normalization_home_dir(self, os_path_exists):
        entry = Entry(mark='test', path='$HOME/tmp')
        self.assertEqual(entry.mark, 'test')
        self.assertEqual(entry.path, '{}/tmp'.format(HOME_DIR))

    def test_init_exception_all_parameters(self):
        with self.assertRaises(ValueError) as cm:
            Entry(path='p', mark='m', entry='e')
        self.assertEqual(
            str(cm.exception),
            'Specify entry OR both path and mark.'
        )

    def test_init_exception_path_and_entry(self):
        with self.assertRaises(ValueError) as cm:
            Entry(path='p', entry='e')
        self.assertEqual(
            str(cm.exception),
            'Specify entry OR both path and mark.'
        )

    def test_init_exception_mark_and_entry(self):
        with self.assertRaises(ValueError) as cm:
            Entry(mark='m', entry='e')
        self.assertEqual(
            str(cm.exception),
            'Specify entry OR both path and mark.'
        )

    def test_init_exception_disallowed_character(self):
        with self.assertRaises(MarkInvalidError) as cm:
            Entry(path='p', mark='ö')
        self.assertEqual(
            str(cm.exception),
            'Invalid mark string: “ö”. Allowed characters for bookmark names '
            'are: “0-9a-zA-Z_”.'
        )

    def test_init_exception_disallowed_character_validate_false(self):
        entry = Entry(path='p', mark='ö', validate=False)
        self.assertEqual(entry.mark, 'ö')

    def test_init_exception_path_non_existent(self):
        with self.assertRaises(NoPathError) as cm:
            Entry(path='xxx', mark='xxx')
        self.assertIn(
            'xxx” doesn’t exist.',
            str(cm.exception)
        )

    def test_init_exception_path_non_existent_validate_false(self):
        entry = Entry(path='xxx', mark='xxx', validate=False)
        self.assertEqual(entry.path, 'xxx')

    def test_method_check_mark(self):
        self.assertEqual(Entry.check_mark('lol'), True)
        self.assertEqual(Entry.check_mark('LOL_lol_123'), True)
        self.assertEqual(Entry.check_mark('l'), True)
        self.assertEqual(Entry.check_mark('1'), True)
        self.assertEqual(Entry.check_mark('_'), True)
        self.assertEqual(Entry.check_mark('l o l'), False)
        self.assertEqual(Entry.check_mark('löl'), False)
        self.assertEqual(Entry.check_mark('l-l'), False)
        self.assertEqual(Entry.check_mark('l,l'), False)

    def test_method_normalize_path(self):
        self.assertNormalizePath('/tmp/lol', '/tmp/lol')
        self.assertNormalizePath('~/.lol', '/home/jf/.lol')
        self.assertNormalizePath('', '')
        self.assertNormalizePath('/', '/')
        self.assertNormalizePath(False, '')
        self.assertNormalizePath('/tmp/', '/tmp')
        self.assertNormalizePath('$HOME/tmp', '/home/jf/tmp')

    def test_method_to_dict(self):
        entry = Entry(mark='test', path='/tmp')
        self.assertEqual(
            entry.to_dict(),
            {'mark': 'test', 'path': '/tmp'}
        )

    def test_method_to_export_string(self):
        entry = Entry(mark='test', path='/tmp')
        self.assertEqual(
            entry.to_export_string(),
            'export DIR_test="/tmp"'
        )

import os
from unittest import TestCase

from shellmarks import MarkInvalidError, ShellmarkEntries

from ._helper import DIR1, DIR2, DIR3, TEST_PATH, tmp_file


class TestClassShellmarkEntries(TestCase):
    def test_init_existent_file(self):
        entries = ShellmarkEntries(path=os.path.join("test", "files", "sdirs"))
        self.assertEqual(entries.entries[0].mark, "dir1")
        self.assertEqual(entries.entries[1].mark, "dir2")
        self.assertEqual(entries.entries[2].mark, "dir3")
        self.assertEqual(entries._index["marks"]["dir1"], [0])
        self.assertEqual(entries._index["marks"]["dir2"], [1])
        self.assertEqual(entries._index["marks"]["dir3"], [2])

    def test_init_non_existent_file(self):
        entries = ShellmarkEntries(path=os.path.join("test", "xxx"))
        self.assertEqual(len(entries.entries), 0)
        self.assertEqual(len(entries._index["marks"]), 0)
        self.assertEqual(len(entries._index["paths"]), 0)

    def test_property_changed(self):
        entries = ShellmarkEntries(path=os.path.join("test", "files", "sdirs"))
        self.assertEqual(entries.changed, False)
        entries.add_entry(mark="dir1", path=DIR1)
        self.assertEqual(entries.changed, True)

    def test_property_changes(self):
        entries = ShellmarkEntries(path=os.path.join("test", "files", "sdirs"))
        self.assertEqual(entries.changes, [])
        entries.delete_entries(mark="dir1")
        self.assertEqual(
            entries.changes, [{"action": "delete", "mark": "dir1", "path": DIR1}]
        )

    def test_method__list_intersection(self):
        list_intersection = ShellmarkEntries._list_intersection
        self.assertEqual(list_intersection([1], [1]), [1])
        self.assertEqual(list_intersection([1], [2]), [])
        self.assertEqual(list_intersection([1, 2], [1, 2]), [1, 2])
        self.assertEqual(list_intersection([2, 1], [1, 2]), [1, 2])
        self.assertEqual(list_intersection([2, 1, 3], [1, 2]), [1, 2])
        self.assertEqual(list_intersection([2, 1, 3], []), [])

    def test_method__store_index_number(self):
        sdirs = tmp_file()
        entries = ShellmarkEntries(path=sdirs)
        entries._store_index_number("mark", "downloads", 7)
        self.assertEqual(entries._index["marks"]["downloads"], [7])

        # The same again
        entries._store_index_number("mark", "downloads", 7)
        self.assertEqual(entries._index["marks"]["downloads"], [7])

        # Add another index number.
        entries._store_index_number("mark", "downloads", 9)
        self.assertEqual(entries._index["marks"]["downloads"], [7, 9])

        # Add a lower index number.
        entries._store_index_number("mark", "downloads", 5)
        self.assertEqual(entries._index["marks"]["downloads"], [5, 7, 9])

        with self.assertRaises(ValueError) as cm:
            entries._store_index_number("lol", "downloads", 1)
        self.assertEqual(str(cm.exception), "attribute_name “lol” unkown.")

    def test_method__update_index(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark="dir1", path=DIR1)
        self.assertEqual(entries._index["marks"]["dir1"], [0])
        self.assertEqual(entries._index["paths"][DIR1], [0])

        # Delete the index store.
        delattr(entries, "_index")
        with self.assertRaises(AttributeError):
            getattr(entries, "_index")

        # Regenerate index.
        entries._update_index()
        self.assertEqual(entries._index["marks"]["dir1"], [0])
        self.assertEqual(entries._index["paths"][DIR1], [0])

    def test_method__get_indexes(self):
        entries = ShellmarkEntries(path=os.path.join("test", "files", "sdirs"))
        self.assertEqual(entries._get_indexes(mark="dir1"), [0])
        self.assertEqual(entries._get_indexes(path=DIR2), [1])
        self.assertEqual(entries._get_indexes(mark="dir3", path=DIR3), [2])

        with self.assertRaises(ValueError) as cm:
            entries._get_indexes(mark="dir1", path=DIR3)
        self.assertIn("mark (dir1) and path", str(cm.exception))

    def test_method_get_entry_by_index(self):
        entries = ShellmarkEntries(path=os.path.join("test", "files", "sdirs"))
        entry = entries.get_entry_by_index(0)
        self.assertEqual(entry.mark, "dir1")
        entry = entries.get_entry_by_index(1)
        self.assertEqual(entry.mark, "dir2")
        entry = entries.get_entry_by_index(2)
        self.assertEqual(entry.mark, "dir3")

    def test_method_get_entries(self):
        entries = ShellmarkEntries(path=os.path.join("test", "files", "sdirs"))
        path = os.path.abspath(os.path.join("test", "files", "dir1"))

        result = entries.get_entries(mark="dir1")
        self.assertEqual(result[0].mark, "dir1")

        result = entries.get_entries(path=path)
        self.assertEqual(result[0].mark, "dir1")

        result = entries.get_entries(mark="dir1", path=path)
        self.assertEqual(result[0].mark, "dir1")

        with self.assertRaises(ValueError) as cm:
            entries.get_entries(mark="dir2", path=path)
        self.assertIn("mark (dir2) and path", str(cm.exception))

        # Get an entry which doesn’t exist by mark.
        self.assertEqual(entries.get_entries(mark="lol"), [])

        # Get an entry which doesn’t exist by path.
        self.assertEqual(entries.get_entries(path="lol"), [])

    def test_method_add_entry(self):
        entries = ShellmarkEntries(path=os.path.join("test", "xxx"))

        entries.add_entry(mark="dir1", path=DIR1)
        self.assertEqual(len(entries.entries), 1)
        self.assertEqual(entries.entries[0].mark, "dir1")
        self.assertEqual(entries._index["marks"]["dir1"], [0])

        entries.add_entry(mark="dir2", path=DIR2)
        self.assertEqual(len(entries.entries), 2)
        self.assertEqual(entries.entries[1].mark, "dir2")
        self.assertEqual(entries._index["marks"]["dir2"], [1])

    def test_method_add_entry_exception(self):
        entries = ShellmarkEntries(path=tmp_file())
        with self.assertRaises(MarkInvalidError):
            entries.add_entry(mark="dör1", path=DIR1)
        with self.assertRaises(MarkInvalidError):
            entries.add_entry(mark="d i r 1", path=DIR1)
        with self.assertRaises(MarkInvalidError):
            entries.add_entry(mark="dir 1", path=DIR1)

    def test_method_add_entry_duplicates(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark="dir1", path=DIR1)
        entries.add_entry(mark="dir1", path=DIR1)
        entries.add_entry(mark="dir1", path=DIR1)
        self.assertEqual(len(entries.entries), 3)
        self.assertEqual(entries._index["marks"]["dir1"], [0, 1, 2])
        self.assertEqual(entries._index["paths"][DIR1], [0, 1, 2])

    def test_method_add_entry_avoid_duplicate_marks(self):
        entries = ShellmarkEntries(path=tmp_file())
        self.assertEqual(entries.add_entry(mark="dir1", path=DIR1), 0)
        self.assertEqual(
            entries.add_entry(mark="dir1", path=DIR1, avoid_duplicate_marks=True), False
        )
        self.assertEqual(len(entries.entries), 1)
        self.assertEqual(
            entries.add_entry(
                mark="dir1",
                path=DIR1,
                avoid_duplicate_marks=True,
                delete_old_entries=True,
            ),
            0,
        )
        self.assertEqual(len(entries.entries), 1)

    def test_method_add_entry_avoid_duplicate_paths(self):
        entries = ShellmarkEntries(path=tmp_file())
        self.assertEqual(entries.add_entry(mark="dir1", path=DIR1), 0)
        self.assertEqual(
            entries.add_entry(mark="dir1", path=DIR1, avoid_duplicate_paths=True), False
        )
        self.assertEqual(len(entries.entries), 1)
        self.assertEqual(
            entries.add_entry(
                mark="dir1",
                path=DIR1,
                avoid_duplicate_paths=True,
                delete_old_entries=True,
            ),
            0,
        )
        self.assertEqual(len(entries.entries), 1)

    def test_method_add_entry_avoid_duplicates(self):
        entries = ShellmarkEntries(path=tmp_file())
        self.assertEqual(entries.add_entry(mark="dir1", path=DIR1), 0)
        self.assertEqual(
            entries.add_entry(
                mark="dir1",
                path=DIR1,
                avoid_duplicate_marks=True,
                avoid_duplicate_paths=True,
            ),
            False,
        )
        self.assertEqual(len(entries.entries), 1)
        self.assertEqual(
            entries.add_entry(
                mark="dir1",
                path=DIR1,
                avoid_duplicate_marks=True,
                avoid_duplicate_paths=True,
                delete_old_entries=True,
            ),
            0,
        )
        self.assertEqual(len(entries.entries), 1)

    def test_method_update_entries(self):
        entries = ShellmarkEntries(path=os.path.join("test", "files", "sdirs"))
        entries.update_entries(old_mark="dir1", new_mark="new1")
        result = entries.get_entries(mark="new1")
        self.assertEqual(result[0].path, DIR1)

    def test_method_update_entries_duplicates(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark="dir1", path=DIR1)
        entries.add_entry(mark="dir1", path=DIR1)
        entries.add_entry(mark="dir1", path=DIR1)
        entries.update_entries(old_mark="dir1", new_mark="new1")
        self.assertEqual(entries._index["marks"]["new1"], [0, 1, 2])
        self.assertEqual(entries._index["paths"][DIR1], [0, 1, 2])

    def test_method_delete_entries(self):
        entries = ShellmarkEntries(path=os.path.join("test", "files", "sdirs"))
        entries.delete_entries(mark="dir1")
        self.assertEqual(len(entries.entries), 2)
        entries.delete_entries(path=DIR2)
        self.assertEqual(len(entries.entries), 1)
        entries.delete_entries(mark="dir3", path=DIR3)
        self.assertEqual(len(entries.entries), 0)

        # Delete entries which don’t exist by mark.
        self.assertEqual(entries.delete_entries(mark="lol"), False)

        # Delete entries which don’t exist by path.
        self.assertEqual(entries.delete_entries(path="lol"), False)

    def test_method_delete_entries_duplicates(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark="dir1", path=DIR1)
        entries.add_entry(mark="dir1", path=DIR1)
        entries.add_entry(mark="dir1", path=DIR1)
        self.assertEqual(len(entries.entries), 3)
        entries.delete_entries(mark="dir1")
        self.assertEqual(len(entries.entries), 0)

    def test_method_delete_duplicates(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark="mark", path=DIR1)
        entries.add_entry(mark="mark", path=DIR2)
        entries.add_entry(mark="other", path=DIR2)
        entries.delete_duplicates(marks=True, paths=False)
        self.assertEqual(entries.entries[0].path, DIR2)
        self.assertEqual(entries.entries[1].path, DIR2)

        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark="mark1", path=DIR1)
        entries.add_entry(mark="mark2", path=DIR1)
        entries.add_entry(mark="mark2", path=DIR2)
        entries.delete_duplicates(marks=False, paths=True)
        self.assertEqual(entries.entries[0].mark, "mark2")
        self.assertEqual(entries.entries[1].mark, "mark2")

        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark="mark1", path=DIR1)
        entries.add_entry(mark="mark1", path=DIR1)
        entries.add_entry(mark="mark2", path=DIR1)
        entries.add_entry(mark="mark1", path=DIR2)
        entries.delete_duplicates(marks=True, paths=True)
        self.assertEqual(len(entries.entries), 2)
        self.assertEqual(entries.entries[0].mark, "mark2")
        self.assertEqual(entries.entries[0].path, DIR1)
        self.assertEqual(entries.entries[1].mark, "mark1")
        self.assertEqual(entries.entries[1].path, DIR2)

    def test_method_sort(self):
        sdirs = tmp_file()
        entries = ShellmarkEntries(path=sdirs)
        entries.add_entry(mark="dir3", path=DIR1)
        entries.add_entry(mark="dir2", path=DIR2)
        entries.add_entry(mark="dir1", path=DIR3)
        self.assertEqual(entries.entries[0].mark, "dir3")
        self.assertEqual(entries.entries[1].mark, "dir2")
        self.assertEqual(entries.entries[2].mark, "dir1")
        self.assertEqual(entries.entries[0].path, DIR1)
        self.assertEqual(entries.entries[1].path, DIR2)
        self.assertEqual(entries.entries[2].path, DIR3)

        entries.sort()
        self.assertEqual(entries.entries[0].mark, "dir1")
        self.assertEqual(entries.entries[1].mark, "dir2")
        self.assertEqual(entries.entries[2].mark, "dir3")

        entries.sort(reverse=True)
        self.assertEqual(entries.entries[0].mark, "dir3")
        self.assertEqual(entries.entries[1].mark, "dir2")
        self.assertEqual(entries.entries[2].mark, "dir1")

        entries.sort(attribute_name="path")
        self.assertEqual(entries.entries[0].path, DIR1)
        self.assertEqual(entries.entries[1].path, DIR2)
        self.assertEqual(entries.entries[2].path, DIR3)

        entries.sort(attribute_name="path", reverse=True)
        self.assertEqual(entries.entries[0].path, DIR3)
        self.assertEqual(entries.entries[1].path, DIR2)
        self.assertEqual(entries.entries[2].path, DIR1)

    def test_method_write(self):
        old_path = os.path.join("test", "files", "sdirs")
        entries = ShellmarkEntries(path=old_path)
        new_path = tmp_file()
        entries.write(new_path=new_path)
        new_path_content = open(new_path, "r").read()
        self.assertTrue(new_path_content)

    def test_combinations(self):
        entries = ShellmarkEntries(path=tmp_file())
        entries.add_entry(mark="dir1", path=DIR1)
        entries.add_entry(mark="dir2", path=DIR2)
        entries.add_entry(mark="dir3", path=DIR3)
        self.assertEqual(entries.get_entries(mark="dir3")[0].path, DIR3)

        # Delete one entry
        entries.delete_entries(mark="dir2")
        self.assertEqual(entries.get_entries(mark="dir3")[0].path, DIR3)

        # Sort
        entries.sort(reverse=True)
        self.assertEqual(entries.get_entries(mark="dir3")[0].path, DIR3)

        # Update one entry
        entries.update_entries(old_mark="dir1", new_path=DIR2)
        self.assertEqual(entries.get_entries(mark="dir3")[0].path, DIR3)

        entries.write()

        content = entries.get_raw()
        self.assertEqual(
            content,
            'export DIR_dir3="{0}/dir3"\nexport DIR_dir1="{0}/dir2"\n'.format(
                TEST_PATH
            ),
        )

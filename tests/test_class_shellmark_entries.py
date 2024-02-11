import os

import pytest

from shellmarks import MarkInvalidError, ShellmarkManager

from ._helper import DIR1, DIR2, DIR3, TEST_PATH, tmp_file


class TestClassShellmarkEntries:
    def test_init_existent_file(self) -> None:
        entries = ShellmarkManager(path=os.path.join("tests", "files", "sdirs"))
        assert entries.entries[0].mark == "dir1"
        assert entries.entries[1].mark == "dir2"
        assert entries.entries[2].mark == "dir3"
        assert entries._index["marks"]["dir1"] == [0]  # type: ignore
        assert entries._index["marks"]["dir2"] == [1]  # type: ignore
        assert entries._index["marks"]["dir3"] == [2]  # type: ignore

    def test_init_non_existent_file(self) -> None:
        entries = ShellmarkManager(path=os.path.join("tests", "xxx"))
        assert len(entries.entries) == 0
        assert len(entries._index["marks"]) == 0  # type: ignore
        assert len(entries._index["paths"]) == 0  # type: ignore

    def test_property_changed(self) -> None:
        entries = ShellmarkManager(path=os.path.join("tests", "files", "sdirs"))
        assert not entries.changed
        entries.add_entry(mark="dir1", path=DIR1)
        assert entries.changed

    def test_property_changes(self) -> None:
        entries = ShellmarkManager(path=os.path.join("tests", "files", "sdirs"))
        assert entries.changes == []
        entries.delete_entries(mark="dir1")
        assert entries.changes == [{"action": "delete", "mark": "dir1", "path": DIR1}]

    def test_method__list_intersection(self) -> None:
        list_intersection = ShellmarkManager._list_intersection  # type: ignore
        assert list_intersection([1], [1]) == [1]
        assert list_intersection([1], [2]) == []
        assert list_intersection([1, 2], [1, 2]) == [1, 2]
        assert list_intersection([2, 1], [1, 2]) == [1, 2]
        assert list_intersection([2, 1, 3], [1, 2]) == [1, 2]
        assert list_intersection([2, 1, 3], []) == []

    def test_method__store_index_number(self) -> None:
        sdirs = tmp_file()
        entries = ShellmarkManager(path=sdirs)
        entries._store_index_number("mark", "downloads", 7)  # type: ignore
        assert entries._index["marks"]["downloads"] == [7]  # type: ignore

        # The same again
        entries._store_index_number("mark", "downloads", 7)  # type: ignore
        assert entries._index["marks"]["downloads"] == [7]  # type: ignore

        # Add another index number.
        entries._store_index_number("mark", "downloads", 9)  # type: ignore
        assert entries._index["marks"]["downloads"] == [7, 9]  # type: ignore

        # Add a lower index number.
        entries._store_index_number("mark", "downloads", 5)  # type: ignore
        assert entries._index["marks"]["downloads"] == [5, 7, 9]  # type: ignore

        # with self.assertRaises(ValueError) as cm:
        #     entries._store_index_number("lol", "downloads", 1)
        # self.assertEqual(str(cm.exception), "attribute_name “lol” unkown.")

    def test_method__update_index(self) -> None:
        entries = ShellmarkManager(path=tmp_file())
        entries.add_entry(mark="dir1", path=DIR1)
        assert entries._index["marks"]["dir1"] == [0]  # type: ignore
        assert entries._index["paths"][DIR1] == [0]  # type: ignore

        # Delete the index store.
        delattr(entries, "_index")
        with pytest.raises(AttributeError):
            getattr(entries, "_index")

        # Regenerate index.
        entries._update_index()  # type: ignore
        assert entries._index["marks"]["dir1"] == [0]  # type: ignore
        assert entries._index["paths"][DIR1] == [0]  # type: ignore

    def test_method__get_indexes(self):
        entries = ShellmarkManager(path=os.path.join("tests", "files", "sdirs"))
        assert entries._get_indexes(mark="dir1") == [0]  # type: ignore
        assert entries._get_indexes(path=DIR2) == [1]  # type: ignore
        assert entries._get_indexes(mark="dir3", path=DIR3) == [2]  # type: ignore

        with pytest.raises(ValueError) as e:
            entries._get_indexes(mark="dir1", path=DIR3)  # type: ignore
        assert "mark (dir1) and path" in e.value.args[0]  # type: ignore

    def test_method_get_entry_by_index(self):
        entries = ShellmarkManager(path=os.path.join("tests", "files", "sdirs"))
        entry = entries.get_entry_by_index(0)
        assert entry.mark == "dir1"
        entry = entries.get_entry_by_index(1)
        assert entry.mark == "dir2"
        entry = entries.get_entry_by_index(2)
        assert entry.mark == "dir3"

    def test_method_get_entries(self):
        entries = ShellmarkManager(path=os.path.join("tests", "files", "sdirs"))
        path = os.path.abspath(os.path.join("tests", "files", "dir1"))

        result = entries.get_entries(mark="dir1")
        assert result[0].mark == "dir1"

        result = entries.get_entries(path=path)
        assert result[0].mark == "dir1"

        result = entries.get_entries(mark="dir1", path=path)
        assert result[0].mark == "dir1"

        with pytest.raises(ValueError) as e:
            entries.get_entries(mark="dir2", path=path)
        assert "mark (dir2) and path" in e.value.args[0]

        # Get an entry which doesn’t exist by mark.
        assert entries.get_entries(mark="lol") == []

        # Get an entry which doesn’t exist by path.
        assert entries.get_entries(path="lol") == []

    def test_method_add_entry(self):
        entries = ShellmarkManager(path=os.path.join("test", "xxx"))

        entries.add_entry(mark="dir1", path=DIR1)
        assert len(entries.entries) == 1
        assert entries.entries[0].mark == "dir1"
        assert entries._index["marks"]["dir1"] == [0]  # type: ignore

        entries.add_entry(mark="dir2", path=DIR2)
        assert len(entries.entries) == 2
        assert entries.entries[1].mark == "dir2"
        assert entries._index["marks"]["dir2"] == [1]  # type: ignore

    def test_method_add_entry_exception(self) -> None:
        entries = ShellmarkManager(path=tmp_file())
        with pytest.raises(MarkInvalidError):
            entries.add_entry(mark="dör1", path=DIR1)
        with pytest.raises(MarkInvalidError):
            entries.add_entry(mark="d i r 1", path=DIR1)
        with pytest.raises(MarkInvalidError):
            entries.add_entry(mark="dir 1", path=DIR1)

    def test_method_add_entry_duplicates(self) -> None:
        entries = ShellmarkManager(path=tmp_file())
        entries.add_entry(mark="dir1", path=DIR1)
        entries.add_entry(mark="dir1", path=DIR1)
        entries.add_entry(mark="dir1", path=DIR1)
        assert len(entries.entries) == 3
        assert entries._index["marks"]["dir1"] == [0, 1, 2]  # type: ignore
        assert entries._index["paths"][DIR1] == [0, 1, 2]  # type: ignore

    def test_method_add_entry_avoid_duplicate_marks(self) -> None:
        entries = ShellmarkManager(path=tmp_file())
        assert entries.add_entry(mark="dir1", path=DIR1) == 0
        assert not entries.add_entry(mark="dir1", path=DIR1, avoid_duplicate_marks=True)

        assert len(entries.entries) == 1
        assert (
            entries.add_entry(
                mark="dir1",
                path=DIR1,
                avoid_duplicate_marks=True,
                delete_old_entries=True,
            )
            == 0
        )
        assert len(entries.entries) == 1

    def test_method_add_entry_avoid_duplicate_paths(self) -> None:
        entries = ShellmarkManager(path=tmp_file())
        assert entries.add_entry(mark="dir1", path=DIR1) == 0
        assert not entries.add_entry(mark="dir1", path=DIR1, avoid_duplicate_paths=True)
        assert len(entries.entries) == 1
        assert (
            entries.add_entry(
                mark="dir1",
                path=DIR1,
                avoid_duplicate_paths=True,
                delete_old_entries=True,
            )
            == 0
        )
        assert len(entries.entries) == 1

    def test_method_add_entry_avoid_duplicates(self) -> None:
        entries = ShellmarkManager(path=tmp_file())
        assert entries.add_entry(mark="dir1", path=DIR1) == 0
        assert not entries.add_entry(
            mark="dir1",
            path=DIR1,
            avoid_duplicate_marks=True,
            avoid_duplicate_paths=True,
        )
        assert len(entries.entries) == 1
        assert (
            entries.add_entry(
                mark="dir1",
                path=DIR1,
                avoid_duplicate_marks=True,
                avoid_duplicate_paths=True,
                delete_old_entries=True,
            )
            == 0
        )
        assert len(entries.entries) == 1

    def test_method_update_entries(self) -> None:
        entries = ShellmarkManager(path=os.path.join("tests", "files", "sdirs"))
        entries.update_entries(old_mark="dir1", new_mark="new1")
        result = entries.get_entries(mark="new1")
        assert result[0].path == DIR1

    def test_method_update_entries_duplicates(self) -> None:
        entries = ShellmarkManager(path=tmp_file())
        entries.add_entry(mark="dir1", path=DIR1)
        entries.add_entry(mark="dir1", path=DIR1)
        entries.add_entry(mark="dir1", path=DIR1)
        entries.update_entries(old_mark="dir1", new_mark="new1")
        assert entries._index["marks"]["new1"] == [0, 1, 2]  # type: ignore
        assert entries._index["paths"][DIR1] == [0, 1, 2]  # type: ignore

    def test_method_delete_entries(self):
        entries = ShellmarkManager(path=os.path.join("tests", "files", "sdirs"))
        entries.delete_entries(mark="dir1")
        assert len(entries.entries) == 2
        entries.delete_entries(path=DIR2)
        assert len(entries.entries) == 1
        entries.delete_entries(mark="dir3", path=DIR3)
        assert len(entries.entries) == 0

        # Delete entries which don’t exist by mark.
        assert not entries.delete_entries(mark="lol")

        # Delete entries which don’t exist by path.
        assert not entries.delete_entries(path="lol")

    def test_method_delete_entries_duplicates(self) -> None:
        entries = ShellmarkManager(path=tmp_file())
        entries.add_entry(mark="dir1", path=DIR1)
        entries.add_entry(mark="dir1", path=DIR1)
        entries.add_entry(mark="dir1", path=DIR1)
        assert len(entries.entries) == 3
        entries.delete_entries(mark="dir1")
        assert len(entries.entries) == 0

    def test_method_delete_duplicates(self) -> None:
        entries = ShellmarkManager(path=tmp_file())
        entries.add_entry(mark="mark", path=DIR1)
        entries.add_entry(mark="mark", path=DIR2)
        entries.add_entry(mark="other", path=DIR2)
        entries.delete_duplicates(marks=True, paths=False)
        assert entries.entries[0].path == DIR2
        assert entries.entries[1].path == DIR2

        entries = ShellmarkManager(path=tmp_file())
        entries.add_entry(mark="mark1", path=DIR1)
        entries.add_entry(mark="mark2", path=DIR1)
        entries.add_entry(mark="mark2", path=DIR2)
        entries.delete_duplicates(marks=False, paths=True)
        assert entries.entries[0].mark == "mark2"
        assert entries.entries[1].mark == "mark2"

        entries = ShellmarkManager(path=tmp_file())
        entries.add_entry(mark="mark1", path=DIR1)
        entries.add_entry(mark="mark1", path=DIR1)
        entries.add_entry(mark="mark2", path=DIR1)
        entries.add_entry(mark="mark1", path=DIR2)
        entries.delete_duplicates(marks=True, paths=True)
        assert len(entries.entries) == 2
        assert entries.entries[0].mark == "mark2"
        assert entries.entries[0].path == DIR1
        assert entries.entries[1].mark == "mark1"
        assert entries.entries[1].path == DIR2

    def test_method_sort(self) -> None:
        sdirs = tmp_file()
        entries = ShellmarkManager(path=sdirs)
        entries.add_entry(mark="dir3", path=DIR1)
        entries.add_entry(mark="dir2", path=DIR2)
        entries.add_entry(mark="dir1", path=DIR3)
        assert entries.entries[0].mark == "dir3"
        assert entries.entries[1].mark == "dir2"
        assert entries.entries[2].mark == "dir1"
        assert entries.entries[0].path == DIR1
        assert entries.entries[1].path == DIR2
        assert entries.entries[2].path == DIR3

        entries.sort()
        assert entries.entries[0].mark == "dir1"
        assert entries.entries[1].mark == "dir2"
        assert entries.entries[2].mark == "dir3"

        entries.sort(reverse=True)
        assert entries.entries[0].mark == "dir3"
        assert entries.entries[1].mark == "dir2"
        assert entries.entries[2].mark == "dir1"

        entries.sort(attribute_name="path")
        assert entries.entries[0].path == DIR1
        assert entries.entries[1].path == DIR2
        assert entries.entries[2].path == DIR3

        entries.sort(attribute_name="path", reverse=True)
        assert entries.entries[0].path == DIR3
        assert entries.entries[1].path == DIR2
        assert entries.entries[2].path == DIR1

    def test_method_write(self) -> None:
        old_path = os.path.join("tests", "files", "sdirs")
        entries = ShellmarkManager(path=old_path)
        new_path = tmp_file()
        entries.write(new_path=new_path)
        new_path_content = open(new_path, "r").read()
        assert new_path_content

    def test_combinations(self) -> None:
        entries = ShellmarkManager(path=tmp_file())
        entries.add_entry(mark="dir1", path=DIR1)
        entries.add_entry(mark="dir2", path=DIR2)
        entries.add_entry(mark="dir3", path=DIR3)
        assert entries.get_entries(mark="dir3")[0].path == DIR3

        # Delete one entry
        entries.delete_entries(mark="dir2")
        assert entries.get_entries(mark="dir3")[0].path == DIR3

        # Sort
        entries.sort(reverse=True)
        assert entries.get_entries(mark="dir3")[0].path == DIR3

        # Update one entry
        entries.update_entries(old_mark="dir1", new_path=DIR2)
        assert entries.get_entries(mark="dir3")[0].path == DIR3

        entries.write()

        content = entries.get_raw()
        assert (
            content
            == 'export DIR_dir3="{0}/dir3"\nexport DIR_dir1="{0}/dir2"\n'.format(
                TEST_PATH
            )
        )

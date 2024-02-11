from unittest import mock

import pytest

from shellmarks import Entry, MarkInvalidError, NoPathError

from ._helper import DIR1, HOME_DIR


class TestClassEntry:
    def assert_normalize_path(self, path: str, result: str) -> None:
        entry = Entry(mark="test", path=DIR1)
        assert entry.normalize_path(path, "/home/jf") == result

    def test_init_by_mark_and_path(self) -> None:
        entry = Entry(mark="test", path="/tmp")
        assert entry.mark == "test"
        assert entry.path == "/tmp"

    def test_init_by_entry(self) -> None:
        entry = Entry(entry='export DIR_test="/tmp"')
        assert entry.mark == "test"
        assert entry.path == "/tmp"

    def test_init_path_normalization_trailing_slash(self) -> None:
        entry = Entry(mark="test", path="/tmp/")
        assert entry.path == "/tmp"

    @mock.patch("os.path.exists")
    def test_init_path_normalization_home_dir(self, _) -> None:
        entry = Entry(mark="test", path="$HOME/tmp")
        assert entry.mark == "test"
        assert entry.path == "{}/tmp".format(HOME_DIR)

    def test_init_exception_all_parameters(self) -> None:
        with pytest.raises(ValueError) as e:
            Entry(path="p", mark="m", entry="e")
        assert e.value.args[0] == "Specify entry OR both path and mark."

    def test_init_exception_path_and_entry(self) -> None:
        with pytest.raises(ValueError) as e:
            Entry(path="p", entry="e")
        assert e.value.args[0] == "Specify entry OR both path and mark."

    def test_init_exception_mark_and_entry(self) -> None:
        with pytest.raises(ValueError) as e:
            Entry(mark="m", entry="e")
        assert e.value.args[0] == "Specify entry OR both path and mark."

    def test_init_exception_disallowed_character(self) -> None:
        with pytest.raises(MarkInvalidError) as e:
            Entry(path="p", mark="ö")
        assert (
            e.value.args[0]
            == "Invalid mark string: “ö”. Allowed characters for bookmark names "
            "are: “0-9a-zA-Z_”."
        )

    def test_init_exception_disallowed_character_validate_false(self) -> None:
        assert Entry(path="p", mark="ö", validate=False).mark == "ö"

    def test_init_exception_path_non_existent(self) -> None:
        with pytest.raises(NoPathError) as e:
            Entry(path="xxx", mark="xxx")
        assert "xxx” doesn’t exist." in e.value.args[0]

    def test_init_exception_path_non_existent_validate_false(self) -> None:
        entry = Entry(path="xxx", mark="xxx", validate=False)
        assert entry.path == "xxx"

    def test_method_check_mark(self) -> None:
        assert Entry.check_mark("lol")
        assert Entry.check_mark("LOL_lol_123")
        assert Entry.check_mark("l")
        assert Entry.check_mark("1")
        assert Entry.check_mark("_")
        assert not Entry.check_mark("l o l")
        assert not Entry.check_mark("löl")
        assert not Entry.check_mark("l-l")
        assert not Entry.check_mark("l,l")

    def test_method_normalize_path(self) -> None:
        self.assert_normalize_path("/tmp/lol", "/tmp/lol")
        self.assert_normalize_path("~/.lol", "/home/jf/.lol")
        self.assert_normalize_path("", "")
        self.assert_normalize_path("/", "/")
        self.assert_normalize_path(False, "")  # type: ignore
        self.assert_normalize_path("/tmp/", "/tmp")
        self.assert_normalize_path("$HOME/tmp", "/home/jf/tmp")

    def test_method_to_dict(self) -> None:
        entry = Entry(mark="test", path="/tmp")
        assert entry.to_dict() == {"mark": "test", "path": "/tmp"}

    def test_method_to_export_string(self) -> None:
        entry = Entry(mark="test", path="/tmp")
        assert entry.to_export_string() == 'export DIR_test="/tmp"'

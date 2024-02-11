from unittest import TestCase

from ._helper import DIR1, DIR2, create_sdirs, mock_main, tmp_file


class TestStatePresent:
    def mock_add(self, mark, path, sdirs=False):
        if not sdirs:
            sdirs = tmp_file()
        return mock_main(
            params={"mark": mark, "path": path, "sdirs": sdirs}, check_mode=False
        )

    def test_present(self):
        mock_objects = mock_main(
            params={"state": "present", "path": DIR1, "mark": "tmp"}
        )
        assert len(mock_objects["entries"].entries) == 1
        entry = mock_objects["entries"].get_entry_by_index(0)
        assert entry.mark == "tmp"
        assert entry.path == DIR1

    def test_add(self):
        mock_objects = self.mock_add("tmp1", DIR1)
        assert len(mock_objects["entries"].entries) == 1
        mock_objects["module"].exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "add", "mark": "tmp1", "path": DIR1},
            ],
        )

    def test_same_entry_not_added(self):
        entries = create_sdirs([["tmp1", DIR1]])
        mock_objects = self.mock_add("tmp1", DIR1, entries.path)
        assert len(mock_objects["entries"].entries) == 1
        mock_objects["module"].exit_json.assert_called_with(changed=False)

    def test_duplicate_mark(self):
        """update mark with new dir"""
        entries = create_sdirs([["tmp1", DIR1]])
        mock_objects = self.mock_add("tmp1", DIR2, entries.path)
        assert len(mock_objects["entries"].entries) == 1
        mock_objects["module"].exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "delete", "mark": "tmp1", "path": DIR1},
                {"action": "add", "mark": "tmp1", "path": DIR2},
            ],
        )

    def test_duplicate_path(self):
        """update path with new mark"""
        entries = create_sdirs([["tmp1", DIR1]])
        mock_objects = self.mock_add("tmp2", DIR1, entries.path)
        assert len(mock_objects["entries"].entries) == 1
        mock_objects["module"].exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "delete", "mark": "tmp1", "path": DIR1},
                {"action": "add", "mark": "tmp2", "path": DIR1},
            ],
        )

    def test_add_second_entry(self):
        entries = create_sdirs([["tmp1", DIR1]])
        mock_objects = self.mock_add("tmp2", DIR2, entries.path)
        assert len(mock_objects["entries"].entries) == 2
        mock_objects["module"].exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "add", "mark": "tmp2", "path": DIR2},
            ],
        )

    def test_non_existent_path(self):
        mock_objects = self.mock_add("tmp4", "/jhkskdflsuizqwewqkfsfdlksjkui")
        mock_objects["module"].fail_json.assert_called_with(
            msg="The path “/jhkskdflsuizqwewqkfsfdlksjkui” doesn’t exist."
        )

    def test_casesensitivity(self):
        entries = create_sdirs([["tmp1", DIR1]])
        mock_objects = self.mock_add("TMP1", DIR2, entries.path)
        assert len(mock_objects["entries"].entries) == 2
        mock_objects["module"].exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "add", "mark": "TMP1", "path": DIR2},
            ],
        )

        mock_objects = self.mock_add("T M P 1", DIR1)
        mock_objects["module"].fail_json.assert_called_with(
            msg="Invalid mark string: “T M P 1”. Allowed characters for "
            "bookmark names are: “0-9a-zA-Z_”."
        )

from typing import Optional

from ._helper import DIR1, DIR2, MockResult, create_sdirs, mock_main, tmp_file


class TestStatePresent:
    def mock_add(self, mark: str, path: str, sdirs: Optional[str] = None) -> MockResult:
        if not sdirs:
            sdirs = tmp_file()
        return mock_main(
            params={"mark": mark, "path": path, "sdirs": sdirs}, check_mode=False
        )

    def test_present(self) -> None:
        result = mock_main(params={"state": "present", "path": DIR1, "mark": "tmp"})
        assert len(result.manager.entries) == 1
        entry = result.manager.get_entry_by_index(0)
        assert entry.mark == "tmp"
        assert entry.path == DIR1

    def test_add(self) -> None:
        result = self.mock_add("tmp1", DIR1)
        assert len(result.manager.entries) == 1
        result.module.exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "add", "mark": "tmp1", "path": DIR1},
            ],
        )

    def test_same_entry_not_added(self) -> None:
        manager = create_sdirs([("tmp1", DIR1)])
        result = self.mock_add("tmp1", DIR1, manager.path)
        assert len(result.manager.entries) == 1
        result.module.exit_json.assert_called_with(changed=False)

    def test_duplicate_mark(self) -> None:
        """update mark with new dir"""
        manager = create_sdirs([("tmp1", DIR1)])
        result = self.mock_add("tmp1", DIR2, manager.path)
        assert len(result.manager.entries) == 1
        result.module.exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "delete", "mark": "tmp1", "path": DIR1},
                {"action": "add", "mark": "tmp1", "path": DIR2},
            ],
        )

    def test_duplicate_path(self) -> None:
        """update path with new mark"""
        manager = create_sdirs([("tmp1", DIR1)])
        result = self.mock_add("tmp2", DIR1, manager.path)
        assert len(result.manager.entries) == 1
        result.module.exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "delete", "mark": "tmp1", "path": DIR1},
                {"action": "add", "mark": "tmp2", "path": DIR1},
            ],
        )

    def test_add_second_entry(self) -> None:
        manager = create_sdirs([("tmp1", DIR1)])
        result = self.mock_add("tmp2", DIR2, manager.path)
        assert len(result.manager.entries) == 2
        result.module.exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "add", "mark": "tmp2", "path": DIR2},
            ],
        )

    def test_non_existent_path(self) -> None:
        result = self.mock_add("tmp4", "/jhkskdflsuizqwewqkfsfdlksjkui")
        result.module.fail_json.assert_called_with(
            msg="The path “/jhkskdflsuizqwewqkfsfdlksjkui” doesn’t exist."
        )

    def test_casesensitivity(self) -> None:
        manager = create_sdirs([("tmp1", DIR1)])
        result = self.mock_add("TMP1", DIR2, manager.path)
        assert len(result.manager.entries) == 2
        result.module.exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "add", "mark": "TMP1", "path": DIR2},
            ],
        )

        result = self.mock_add("T M P 1", DIR1)
        result.module.fail_json.assert_called_with(
            msg="Invalid mark string: “T M P 1”. Allowed characters for "
            "bookmark names are: “0-9a-zA-Z_”."
        )

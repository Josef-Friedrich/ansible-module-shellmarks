from ._helper import DIR1, DIR2, DIR3, MockResult, mock_main, tmp_file


class TestStateAbsent:
    def setup_method(self) -> None:
        self.sdirs = tmp_file()
        self.mock_add("tmp1", DIR1)
        self.mock_add("tmp2", DIR2)
        self.mock_add("tmp3", DIR3)

    def mock_add(self, mark: str, path: str) -> MockResult:
        return mock_main(
            params={"mark": mark, "path": path, "sdirs": self.sdirs}, check_mode=False
        )

    def test_delete_by_mark(self) -> None:
        result = mock_main(
            {
                "sdirs": self.sdirs,
                "mark": "tmp1",
                "state": "absent",
            }
        )
        assert len(result.manager.entries) == 2
        result.module.exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "delete", "mark": "tmp1", "path": DIR1},
            ],
        )

    def test_delete_nonexistent(self) -> None:
        non_existent = "/tmp/tmp34723423643646346etfjf34gegf623646"
        result = mock_main(
            {"sdirs": self.sdirs, "path": non_existent, "state": "absent"}
        )
        assert len(result.manager.entries) == 3
        result.module.exit_json.assert_called_with(changed=False)

    def test_delete_by_path(self) -> None:
        result = mock_main({"sdirs": self.sdirs, "path": DIR1, "state": "absent"})
        assert len(result.manager.entries) == 2
        result.module.exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "delete", "mark": "tmp1", "path": DIR1},
            ],
        )

    def test_delete_by_path_and_mark(self) -> None:
        result = mock_main(
            {"sdirs": self.sdirs, "mark": "tmp1", "path": DIR1, "state": "absent"}
        )
        assert len(result.manager.entries) == 2
        result.module.exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "delete", "mark": "tmp1", "path": DIR1},
            ],
        )

    def test_delete_casesensitivity(self) -> None:
        result = mock_main({"sdirs": self.sdirs, "mark": "TMP1", "state": "absent"})
        assert len(result.manager.entries) == 3
        result.module.exit_json.assert_called_with(changed=False)

    def test_delete_on_empty_sdirs_by_mark(self) -> None:
        result = mock_main({"sdirs": tmp_file(), "mark": "dir1", "state": "absent"})
        result.module.exit_json.assert_called_with(changed=False)

    def test_delete_on_empty_sdirs_by_path(self) -> None:
        result = mock_main({"sdirs": tmp_file(), "path": "/dir1", "state": "absent"})
        result.module.exit_json.assert_called_with(changed=False)

    def test_delete_on_empty_sdirs_by_path_and_mark(self) -> None:
        result = mock_main(
            {"sdirs": tmp_file(), "mark": "dir1", "path": "/dir1", "state": "absent"}
        )
        result.module.exit_json.assert_called_with(changed=False)

    def test_delete_all_options_true(self) -> None:
        result = mock_main(
            {
                "sdirs": self.sdirs,
                "state": "absent",
                "delete_duplicates": True,
                "path": DIR1,
                "mark": "tmp1",
                "sorted": True,
                "cleanup": True,
            },
            check_mode=False,
        )

        assert len(result.manager.entries) == 2
        result.module.exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    "action": "delete",
                    "mark": "tmp1",
                    "path": DIR1,
                },
                {
                    "action": "sort",
                    "sort_by": "mark",
                    "reverse": False,
                },
            ],
        )

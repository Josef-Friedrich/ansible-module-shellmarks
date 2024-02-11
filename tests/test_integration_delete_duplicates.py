from ._helper import DIR1, DIR2, DIR3, create_sdirs, mock_main


class TestSortTrue:
    @staticmethod
    def create_sdirs_file():
        entries = create_sdirs(
            [
                ("dir1", DIR1),
                ("dir2", DIR1),
                ("dir2", DIR2),
                ("dir3", DIR3),
            ]
        )
        return entries.path

    def test_delete_duplicates_true_check_mode_true(self):
        sdirs = self.create_sdirs_file()
        result = mock_main(
            params={"delete_duplicates": True, "sdirs": sdirs}, check_mode=True
        )
        assert result.manager.entries[0].mark == "dir1"
        assert result.manager.entries[0].path == DIR1
        assert result.manager.entries[1].mark == "dir2"
        assert result.manager.entries[1].path == DIR1
        assert len(result.manager.entries) == 4
        result.module.exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "delete", "mark": "dir2", "path": DIR1},
                {"action": "delete_duplicates", "count": 1},
            ],
        )

    def test_delete_duplicates_true_check_mode_false(self):
        sdirs = self.create_sdirs_file()
        result = mock_main(
            params={"delete_duplicates": True, "sdirs": sdirs}, check_mode=False
        )
        assert result.manager.entries[0].mark == "dir1"
        assert result.manager.entries[0].path == DIR1
        assert result.manager.entries[1].mark == "dir2"
        assert result.manager.entries[1].path == DIR2
        assert len(result.manager.entries) == 3
        result.module.exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "delete", "mark": "dir2", "path": DIR1},
                {"action": "delete_duplicates", "count": 1},
            ],
        )

    def test_delete_duplicates_false_check_mode_true(self):
        sdirs = self.create_sdirs_file()
        result = mock_main(
            params={"delete_duplicates": False, "sdirs": sdirs}, check_mode=True
        )
        assert result.manager.entries[0].mark == "dir1"
        assert result.manager.entries[0].path == DIR1
        assert result.manager.entries[1].mark == "dir2"
        assert result.manager.entries[1].path == DIR1
        assert len(result.manager.entries) == 4
        result.module.exit_json.assert_called_with(changed=False)

    def test_delete_duplicates_false_check_mode_false(self):
        sdirs = self.create_sdirs_file()
        result = mock_main(
            params={"delete_duplicates": False, "sdirs": sdirs}, check_mode=False
        )
        assert result.manager.entries[0].mark == "dir1"
        assert result.manager.entries[0].path == DIR1
        assert result.manager.entries[1].mark == "dir2"
        assert result.manager.entries[1].path == DIR1
        assert len(result.manager.entries) == 4
        result.module.exit_json.assert_called_with(changed=False)

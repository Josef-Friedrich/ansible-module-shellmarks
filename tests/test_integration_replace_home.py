from ._helper import DIR1, HOME_DIR, create_sdirs, mock_main, read


class TestReplaceHome:
    @staticmethod
    def create_sdirs_file() -> str:
        entries = create_sdirs([("home", HOME_DIR)])
        return entries.path

    def test_replace_home_true_check_mode_false(self) -> None:
        sdirs = self.create_sdirs_file()
        result = mock_main(
            params={"replace_home": True, "sdirs": sdirs}, check_mode=False
        )

        lines = read(sdirs)
        assert "$HOME" in lines[0]
        result.module.exit_json.assert_called_with(changed=True)

    def test_replace_home_true_state_present_check_mode_false(self) -> None:
        sdirs = self.create_sdirs_file()
        result = mock_main(
            params={
                "replace_home": True,
                "sdirs": sdirs,
                "path": DIR1,
                "mark": "dir1",
            },
            check_mode=False,
        )

        lines = read(sdirs)
        assert "$HOME" in lines[0]
        result.module.exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    "action": "add",
                    "mark": "dir1",
                    "path": DIR1,
                },
            ],
        )

    def test_replace_home_true_check_mode_true(self) -> None:
        sdirs = self.create_sdirs_file()
        result = mock_main(
            params={"replace_home": True, "sdirs": sdirs}, check_mode=True
        )

        lines = read(sdirs)
        assert "$HOME" not in lines[0]
        result.module.exit_json.assert_called_with(changed=True)

    def test_replace_home_true_state_present_check_mode_true(self) -> None:
        sdirs = self.create_sdirs_file()
        result = mock_main(
            params={
                "replace_home": True,
                "sdirs": sdirs,
                "path": DIR1,
                "mark": "dir1",
            },
            check_mode=True,
        )

        lines = read(sdirs)
        assert "$HOME" not in lines[0]
        result.module.exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    "action": "add",
                    "mark": "dir1",
                    "path": DIR1,
                },
            ],
        )

    def test_replace_home_false_check_mode_false(self) -> None:
        sdirs = self.create_sdirs_file()
        result = mock_main(
            params={"replace_home": False, "sdirs": sdirs}, check_mode=False
        )

        lines = read(sdirs)
        assert "$HOME" not in lines[0]
        result.module.exit_json.assert_called_with(changed=False)

    def test_replace_home_false_state_present_check_mode_false(self) -> None:
        sdirs = self.create_sdirs_file()
        result = mock_main(
            params={
                "replace_home": False,
                "sdirs": sdirs,
                "path": DIR1,
                "mark": "dir1",
            },
            check_mode=False,
        )

        lines = read(sdirs)
        assert "$HOME" not in lines[0]
        result.module.exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    "action": "add",
                    "mark": "dir1",
                    "path": DIR1,
                },
            ],
        )

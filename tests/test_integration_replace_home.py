from unittest import TestCase

from ._helper import DIR1, HOME_DIR, create_sdirs, mock_main, read


class TestReplaceHome:
    @staticmethod
    def create_sdirs_file():
        entries = create_sdirs([["home", HOME_DIR]])
        return entries.path

    def test_replace_home_true_check_mode_false(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(
            params={"replace_home": True, "sdirs": sdirs}, check_mode=False
        )

        lines = read(sdirs)
        assert "$HOME" in lines[0]
        mock_objects["module"].exit_json.assert_called_with(changed=True)

    def test_replace_home_true_state_present_check_mode_false(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(
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
        mock_objects["module"].exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    "action": "add",
                    "mark": "dir1",
                    "path": DIR1,
                },
            ],
        )

    def test_replace_home_true_check_mode_true(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(
            params={"replace_home": True, "sdirs": sdirs}, check_mode=True
        )

        lines = read(sdirs)
        assert "$HOME" not in lines[0]
        mock_objects["module"].exit_json.assert_called_with(changed=True)

    def test_replace_home_true_state_present_check_mode_true(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(
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
        mock_objects["module"].exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    "action": "add",
                    "mark": "dir1",
                    "path": DIR1,
                },
            ],
        )

    def test_replace_home_false_check_mode_false(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(
            params={"replace_home": False, "sdirs": sdirs}, check_mode=False
        )

        lines = read(sdirs)
        assert "$HOME" not in lines[0]
        mock_objects["module"].exit_json.assert_called_with(changed=False)

    def test_replace_home_false_state_present_check_mode_false(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(
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
        mock_objects["module"].exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    "action": "add",
                    "mark": "dir1",
                    "path": DIR1,
                },
            ],
        )

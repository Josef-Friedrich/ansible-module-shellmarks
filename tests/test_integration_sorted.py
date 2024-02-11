from unittest import TestCase

from ._helper import DIR1, DIR2, DIR3, create_sdirs, mock_main


class TestSortTrue:
    @staticmethod
    def create_sdirs_file():
        entries = create_sdirs(
            [
                ["dirB", DIR2],
                ["dirC", DIR3],
                ["dirA", DIR1],
            ]
        )
        return entries.path

    def test_sorted_true_check_mode_true(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(
            params={"sorted": True, "sdirs": sdirs}, check_mode=True
        )
        assert mock_objects["entries"].entries[0].mark == "dirB"
        mock_objects["module"].exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    "action": "sort",
                    "sort_by": "mark",
                    "reverse": False,
                },
            ],
        )

    def test_sorted_true_check_mode_false(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(
            params={"sorted": True, "sdirs": sdirs}, check_mode=False
        )
        assert mock_objects["entries"].entries[0].mark == "dirA"
        assert mock_objects["entries"].entries[1].mark == "dirB"
        assert mock_objects["entries"].entries[2].mark == "dirC"
        assert mock_objects["entries"].entries[2].mark == "dirC"
        mock_objects["module"].exit_json.assert_called_with(
            changed=True,
            changes=[
                {
                    "action": "sort",
                    "sort_by": "mark",
                    "reverse": False,
                },
            ],
        )

    def test_sorted_false_check_mode_true(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(
            params={"sorted": False, "sdirs": sdirs}, check_mode=True
        )
        assert mock_objects["entries"].entries[0].mark == "dirB"
        assert mock_objects["entries"].entries[1].mark == "dirC"
        assert mock_objects["entries"].entries[2].mark == "dirA"
        mock_objects["module"].exit_json.assert_called_with(changed=False)

    def test_sorted_false_check_mode_false(self):
        sdirs = self.create_sdirs_file()
        mock_objects = mock_main(
            params={"sorted": False, "sdirs": sdirs}, check_mode=False
        )
        assert mock_objects["entries"].entries[0].mark == "dirB"
        assert mock_objects["entries"].entries[1].mark == "dirC"
        assert mock_objects["entries"].entries[2].mark == "dirA"
        mock_objects["module"].exit_json.assert_called_with(changed=False)

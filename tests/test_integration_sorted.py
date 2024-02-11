from ._helper import DIR1, DIR2, DIR3, create_sdirs, mock_main


class TestSortTrue:
    @staticmethod
    def create_sdirs_file():
        entries = create_sdirs(
            [
                ("dirB", DIR2),
                ("dirC", DIR3),
                ("dirA", DIR1),
            ]
        )
        return entries.path

    def test_sorted_true_check_mode_true(self):
        sdirs = self.create_sdirs_file()
        result = mock_main(params={"sorted": True, "sdirs": sdirs}, check_mode=True)
        assert result.manager.entries[0].mark == "dirB"
        result.module.exit_json.assert_called_with(
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
        result = mock_main(params={"sorted": True, "sdirs": sdirs}, check_mode=False)
        assert result.manager.entries[0].mark == "dirA"
        assert result.manager.entries[1].mark == "dirB"
        assert result.manager.entries[2].mark == "dirC"
        assert result.manager.entries[2].mark == "dirC"
        result.module.exit_json.assert_called_with(
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
        result = mock_main(params={"sorted": False, "sdirs": sdirs}, check_mode=True)
        assert result.manager.entries[0].mark == "dirB"
        assert result.manager.entries[1].mark == "dirC"
        assert result.manager.entries[2].mark == "dirA"
        result.module.exit_json.assert_called_with(changed=False)

    def test_sorted_false_check_mode_false(self):
        sdirs = self.create_sdirs_file()
        result = mock_main(params={"sorted": False, "sdirs": sdirs}, check_mode=False)
        assert result.manager.entries[0].mark == "dirB"
        assert result.manager.entries[1].mark == "dirC"
        assert result.manager.entries[2].mark == "dirA"
        result.module.exit_json.assert_called_with(changed=False)

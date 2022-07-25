from unittest import TestCase

from _helper import DIR1, DIR2, DIR3, mock_main, tmp_file


class TestStateAbsent(TestCase):
    def setUp(self):
        self.sdirs = tmp_file()
        self.mock_add("tmp1", DIR1)
        self.mock_add("tmp2", DIR2)
        self.mock_add("tmp3", DIR3)

    def mock_add(self, mark, path):
        return mock_main(
            params={"mark": mark, "path": path, "sdirs": self.sdirs}, check_mode=False
        )

    def test_delete_by_mark(self):
        mock_objects = mock_main(
            {
                "sdirs": self.sdirs,
                "mark": "tmp1",
                "state": "absent",
            }
        )
        self.assertEqual(len(mock_objects["entries"].entries), 2)
        mock_objects["module"].exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "delete", "mark": "tmp1", "path": DIR1},
            ],
        )

    def test_delete_nonexistent(self):
        non_existent = "/tmp/tmp34723423643646346etfjf34gegf623646"
        mock_objects = mock_main(
            {"sdirs": self.sdirs, "path": non_existent, "state": "absent"}
        )
        self.assertEqual(len(mock_objects["entries"].entries), 3)
        mock_objects["module"].exit_json.assert_called_with(changed=False)

    def test_delete_by_path(self):
        mock_objects = mock_main({"sdirs": self.sdirs, "path": DIR1, "state": "absent"})
        self.assertEqual(len(mock_objects["entries"].entries), 2)
        mock_objects["module"].exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "delete", "mark": "tmp1", "path": DIR1},
            ],
        )

    def test_delete_by_path_and_mark(self):
        mock_objects = mock_main(
            {"sdirs": self.sdirs, "mark": "tmp1", "path": DIR1, "state": "absent"}
        )
        self.assertEqual(len(mock_objects["entries"].entries), 2)
        mock_objects["module"].exit_json.assert_called_with(
            changed=True,
            changes=[
                {"action": "delete", "mark": "tmp1", "path": DIR1},
            ],
        )

    def test_delete_casesensitivity(self):
        mock_objects = mock_main(
            {"sdirs": self.sdirs, "mark": "TMP1", "state": "absent"}
        )
        self.assertEqual(len(mock_objects["entries"].entries), 3)
        mock_objects["module"].exit_json.assert_called_with(changed=False)

    def test_delete_on_empty_sdirs_by_mark(self):
        mock_objects = mock_main(
            {"sdirs": tmp_file(), "mark": "dir1", "state": "absent"}
        )
        mock_objects["module"].exit_json.assert_called_with(changed=False)

    def test_delete_on_empty_sdirs_by_path(self):
        mock_objects = mock_main(
            {"sdirs": tmp_file(), "path": "/dir1", "state": "absent"}
        )
        mock_objects["module"].exit_json.assert_called_with(changed=False)

    def test_delete_on_empty_sdirs_by_path_and_mark(self):
        mock_objects = mock_main(
            {"sdirs": tmp_file(), "mark": "dir1", "path": "/dir1", "state": "absent"}
        )
        mock_objects["module"].exit_json.assert_called_with(changed=False)

    def test_delete_all_options_true(self):
        mock_objects = mock_main(
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

        self.assertEqual(len(mock_objects["entries"].entries), 2)
        mock_objects["module"].exit_json.assert_called_with(
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

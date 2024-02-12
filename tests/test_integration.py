from unittest import mock

from shellmarks import ShellmarkManager

from ._helper import DIR1, HOME_DIR, mock_main, read, tmp_file


class TestErrors:
    module: mock.MagicMock
    manager: ShellmarkManager
    sdirs: str

    @classmethod
    def setup_class(cls) -> None:
        cls.sdirs = tmp_file()

    def mock_add(self, mark: str, path: str) -> None:
        result = mock_main(
            params={"mark": mark, "path": path, "sdirs": self.sdirs}, check_mode=False
        )
        self.module: mock.MagicMock = result.module
        self.manager = result.manager

    def test_error_dash(self) -> None:
        self.mock_add(mark="l-l", path=DIR1)
        self.module.fail_json.assert_called_with(
            msg="Invalid mark string: “l-l”. Allowed characters for bookmark "
            "names are: “0-9a-zA-Z_”."
        )

    def test_error_blank_space(self) -> None:
        self.mock_add(mark="l l", path=DIR1)
        self.module.fail_json.assert_called_with(
            msg="Invalid mark string: “l l”. Allowed characters for bookmark "
            "names are: “0-9a-zA-Z_”."
        )

    def test_error_umlaut(self) -> None:
        self.mock_add(mark="löl", path=DIR1)
        self.module.fail_json.assert_called_with(
            msg="Invalid mark string: “löl”. Allowed characters for bookmark "
            "names are: “0-9a-zA-Z_”."
        )

    def test_error_comma(self) -> None:
        self.mock_add(mark="l,l", path=DIR1)
        self.module.fail_json.assert_called_with(
            msg="Invalid mark string: “l,l”. Allowed characters for bookmark "
            "names are: “0-9a-zA-Z_”."
        )


class TestParams:
    def test_mock(self) -> None:
        sdirs = tmp_file()
        result = mock_main(
            {
                "cleanup": False,
                "delete_duplicates": False,
                "export": None,
                "export_check": None,
                "mark": "dir1",
                "path": DIR1,
                "replace_home": True,
                "sdirs": sdirs,
                "sorted": False,
                "state": "present",
            },
            check_mode=False,
        )

        expected = dict(
            cleanup=dict(default=False, type="bool"),
            delete_duplicates=dict(default=False, type="bool"),
            export=dict(type="str"),
            export_check=dict(type="str"),
            mark=dict(aliases=["bookmark"]),
            path=dict(aliases=["src"]),
            replace_home=dict(default=True, type="bool"),
            sdirs=dict(default="~/.sdirs"),
            sorted=dict(default=True, type="bool"),
            state=dict(default="present", choices=["present", "absent"]),
        )

        assert (
            mock.call(argument_spec=expected, supports_check_mode=True)
            == result.AnsibleModule.call_args
        )

        lines = read(sdirs)
        result_path = DIR1.replace(HOME_DIR, "$HOME")
        assert lines[0] == 'export DIR_dir1="{}"\n'.format(result_path)

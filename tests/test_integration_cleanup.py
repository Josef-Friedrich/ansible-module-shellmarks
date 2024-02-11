from shellmarks import ShellmarkManager

from ._helper import (
    DIR1,
    DIR2,
    DIR3,
    create_tmp_text_file_with_content,
    mock_main,
    tmp_dir,
    tmp_file,
)


class TestCleanup:
    def test_cleanup(self):
        path = tmp_dir()
        no = 'export DIR_tmpb="/tmpXDR34723df4WER/d4REd4RE64er64erb"\n'
        content = no + no + no + 'export DIR_exists="' + path + '"\n' + no + no + no
        sdirs = create_tmp_text_file_with_content(content)

        result = mock_main({"cleanup": True, "sdirs": sdirs})
        assert len(result.manager.entries) == 1
        assert result.manager.entries[0].path == path

        result.module.exit_json.assert_called_with(
            changed=True, changes=[{"action": "cleanup", "count": 6}]
        )

    def test_nothing_to_do(self):
        entries = ShellmarkManager(path=tmp_file())
        entries.add_entry(mark="dir1", path=DIR1)
        entries.add_entry(mark="dir2", path=DIR2)
        entries.add_entry(mark="dir3", path=DIR3)
        entries.write()

        result = mock_main({"cleanup": True, "sdirs": entries.path})

        entries = ShellmarkManager(path=result.module.params["sdirs"])
        assert len(result.manager.entries) == 3
        assert result.manager.entries[0].path == DIR1

        result.module.exit_json.assert_called_with(changed=False)

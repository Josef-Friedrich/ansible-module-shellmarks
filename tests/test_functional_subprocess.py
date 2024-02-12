import os
import subprocess
from unittest import skip

old_env = os.getenv("ANSIBLE_LIBRARY")

if old_env:
    os.putenv("ANSIBLE_LIBRARY", old_env + ":" + os.getcwd())
else:
    os.putenv("ANSIBLE_LIBRARY", os.getcwd())


class TestFunctionalWithSubprocess:
    def test_ansible_doc(self) -> None:
        output = subprocess.check_output(
            ["ansible-doc", "shellmarks"], encoding="utf-8"
        )
        assert "commonly used directories" in output

    @skip("Figure out ansible-playbook in tox environment?")
    def test_ansible_playbook(self) -> None:
        output = subprocess.run(
            [
                "ansible-playbook",
                "-l",
                "localhost,",
                "-c",
                "local",
                os.path.join(os.getcwd(), "play.yml"),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            shell=True,
        )
        assert "Add a shellmark for the home folder" in output.stdout

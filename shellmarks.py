#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017-2024, Josef Friedrich <josef@friedrich.rocks>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

import os
import pwd
import re
import shlex
import subprocess
from typing import List, Literal, Optional, TypedDict, cast

from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    "metadata_version": "1.0",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: shellmarks
short_description: |
    A module to set bookmarks to commonly used directories like the tools
    shellmarks / bashmarks do.
description:
    - shellmarks U(https://github.com/Bilalh/shellmarks) bashmarks
      U(https://github.com/huyng/bashmarks) are shell scripts that allows
      you to save and jump to commonly used directories with tab
      completion.

author: "Josef Friedrich (@Josef-Friedrich)"
options:
    cleanup:
        description:
            - Delete bookmarks of nonexistent directories.
        required: false
        default: false
    delete_duplicates:
        description:
            - Delete duplicate bookmark entries. This option deletes both
              duplicate mark and duplicate path entries. Entries at the
              beginning are deleted, entries at the end are perserved.
        required: false
        default: false
    export:
        description:
            - Command line string to export the bookmarks. The string
              %mark is replaced with the mark and %path is replaced with
              the path. For example 'autojump --add %path' or 'zoxide add
              %path'.
        required: false
    export_query:
        description:
            - Command line string to query if the bookmark is already exported.
              The string %mark is replaced with the mark and %path is replaced
              with the path. For example 'zoxide query %path'.
        required: false
    mark:
        description:
            - Name of the bookmark.
        required: false
        aliases:
            - bookmark
    path:
        description:
            - Full path to the directory.
        required: false
        aliases:
            - src
    replace_home:
        description:
            - Replace home directory with $HOME variable.
        required: false
        default: true
    sdirs:
        description:
            - The path to the file where the bookmarks are stored.
        required: false
        default: ~/.sdirs
    sorted:
        description:
            - Sort entries in the bookmark file.
        required: false
        default: true
    state:
        description:
            - State of the mark.
        required: false
        default: present
        choices:
            - present
            - absent
        aliases:
            - src
"""

RETURN = """
changes:
    description: A list of actions
    returned: On changed
    type: list
    sample:
      - action: add
        mark: dir1
        path: /dir1
      - action: delete
        mark: dir1
        path: /dir1
      - action: sort
        sort_by: mark
        reverse: false
      - action: cleanup
        count: 1
"""

EXAMPLES = """
# Bookmark the ansible configuration directory
- shellmarks:
    mark: ansible
    path: /etc/ansible
    state: present

# Delete bookmark of the ansible configuration directory
- shellmarks:
    mark: ansible
    path: /etc/ansible
    state: absent

# Replace home directory with $HOME variable
- shellmarks:
    replace_home: true

# Sort entries in the bookmark file
- shellmarks:
    sorted: true

# Delete bookmarks of no longer existing directories
- shellmarks:
    cleanup: true
"""


class ShellmarksError(Exception):
    """Base class for other exceptions"""


class MarkInvalidError(ShellmarksError):
    """Raised when the mark contains invalid characters."""


class NoPathError(ShellmarksError):
    """Raised when the path to bookmark is non-existent."""


class Entry:
    """A object representation of one line in the `~/.sdirs` file.

    :param mark: The name of the bookmark / shellmark.
    :param path: The path of the bookmark / shellmark.
    :param entry: One line in the file `~/.sdirs`
      (export DIR_dir1="/dir1").
    :param validate: Validate the input. Raise some exceptions if
      the bookmark strings are invalid or if the paths don’t exist.

    :raises ValueError: If not all necessary class arguments are specified.
    :raises MarkInvalidError: If `validate=True` and the given mark contains
      invalid characters.
    :raises NoPathError: If `validate=True` and the given path doesn’t exist.
    """

    mark: str
    """The name of the bookmark."""

    path: str
    """The path which should be bookmark."""

    _home_dir: str
    """The path of the home directory."""

    def __init__(
        self, path: str = "", mark: str = "", entry: str = "", validate: bool = True
    ) -> None:
        self.mark = ""

        self.path = ""

        if entry and (path or mark):
            raise ValueError("Specify entry OR both path and mark.")

        if (path and not mark) or (mark and not path):
            raise ValueError("Specify both variables: path and mark")

        if entry:
            match = self.parse_entry(entry)
            self.mark = match[0]
            self.path = match[1]
        else:
            self.mark = mark
            self.path = path

        if validate and not self.check_mark(self.mark):
            message = (
                "Invalid mark string: “{}”. "
                + "Allowed characters for bookmark names are: "
                + "“0-9a-zA-Z_”."
            )
            raise MarkInvalidError(message.format(self.mark))

        self._home_dir = pwd.getpwuid(os.getuid()).pw_dir

        self.path = self.normalize_path(self.path, self._home_dir)

        if validate and not os.path.exists(self.path):
            raise NoPathError("The path “{}” doesn’t exist.".format(self.path))

    @staticmethod
    def parse_entry(entry: str):
        """Extract from a entry line the name of the bookmark and the path.

        :param string entry: One line in the file ~/.sdirs
          (export DIR_dir1="/dir1").

        :return: A match tuple
        :rtype: tuple
        """
        return re.findall(r'export DIR_(.*)="(.*)"', entry)[0]

    @staticmethod
    def check_mark(mark: str) -> bool:
        """
        Check if a bookmark string is valid.

        :param mark: The name of the bookmark / shellmark.

        :return: True if the bookmark contains no invalid characters, false
          otherwise.
        :rtype: boolean"""
        regex = re.compile(r"^[0-9a-zA-Z_]+$")
        match = regex.match(str(mark))
        if match:
            return match.group(0) == mark
        return False

    @staticmethod
    def normalize_path(path: str, home_dir: str) -> str:
        """Replace ~ and $HOME with a the actual path string. Replace trailing
        slashes. Convert to a absolute path.

        :param string path: The path of the bookmark / shellmark.
        :param string home_dir: The path of the home directory.

        :return: A normalized path string.
        :rtype: string
        """
        if path:
            path = re.sub(r"(.+)/?$", r"\1", path)
            path = re.sub(r"^~", home_dir, path)
            path = re.sub(r"^\$HOME", home_dir, path)
            # Only existing paths should converted to absolute paths.
            if os.path.exists(path):
                path = os.path.abspath(path)
            return path
        return ""

    def to_dict(self) -> dict[str, str]:
        """Bundle the two public attributes of this class into a dictonary.
        It is not possible to use the magic method __dict__ because this
        method also includes private attributes.

        :return: A dictionary with two keys: mark and path
        :rtype: dict
        """
        return {"mark": self.mark, "path": self.path}

    def to_export_string(self, replace_home: bool = False) -> str:
        """Assemble the attributes `mark` and `path` to entry line
        (export DIR_mark="path").

        :param boolean replace_home: Replace the home directory with the
          environment variable $HOME.

        :return: The export string (export ...)
        :rtype: string
        """
        if replace_home:
            path = self.path.replace(self._home_dir, "$HOME")
        else:
            path = self.path
        return 'export DIR_{}="{}"'.format(self.mark, path)

    def __expand_command(self, command: str) -> list[str]:
        args: list[str] = shlex.split(command)
        for i in range(len(args)):
            args[i] = args[i].replace("%path", self.path).replace("%mark", self.mark)
        return args

    def run_command(self, command: str) -> Optional[str]:
        args = self.__expand_command(command)
        result = subprocess.run(
            args,
            capture_output=True,
            encoding="utf-8",
        )
        if result.returncode == 0:
            return shlex.join(args)
        return None


class ShellmarkManager:
    """A class to store, add, get, update and delete shellmark entries.

    :param string path: The path of the text file where all shellmark
      entries are stored.

    :param boolean validate_on_init: Validate the attributes `mark` and
      `path` on object initialisation.
    """

    path: str
    """The path of the .sdirs file."""

    entries: list[Entry]
    """A list of shellmark entries. """

    _index: dict[str, dict[str, list[int]]]
    """A collection of dictionaries to hold the indexes (position of
    the single entries in the list of entries).

    key: marks

    A dictonary: The key is the bookmark / shellmark name and the value is
    a list of the corresponding index numbers.

    key: paths

    A dictonary: The key is the path and the value is a list
    the corresponding index numbers
    """

    changes: list[dict[str, str | int | list[str]]]
    """A list of changes. Each change is a dictonary with the keys
    action, mark, path"""

    _lines_original: list[str]
    """The render lines of the origin sdirs file"""

    replace_home: bool
    """Replace the home folder with the variable $HOME."""

    __export_commands: list[str]

    _entries_original: list[Entry]
    """A copy of the unmodified list entires generated by the object
    initialisation."""

    def __init__(self, path: str, validate_on_init: bool = True) -> None:
        self.path = path

        self.entries = []

        self._index = {
            "marks": {},
            "paths": {},
        }

        self.changes = []

        self._lines_original = []

        self.replace_home = False

        if os.path.isfile(path):
            sdirs = open(self.path, "r")
            self._lines_original = sdirs.readlines()
            sdirs.close()

        for line in self._lines_original:
            self.add_entry(entry_line=line, validate=validate_on_init)

        self._entries_original = list(self.entries)
        self.__export_commands = []

    @property
    def changed(self) -> bool:
        """True if the shellmark entries are changed ofter the object
        initialisation. It is not possible to use normal == comparison hence
        the entry objects are regenerated by some actions (cleanup,
        delete_duplicates).
        """
        if len(self.__export_commands) > 0:
            return True
        if len(self._entries_original) != len(self.entries):
            return True

        lines_new: list[str] = []

        for entry in self.entries:
            lines_new.append(
                entry.to_export_string(replace_home=self.replace_home) + "\n"
            )

        if self._lines_original != lines_new:
            return True

        return False

    @staticmethod
    def _list_intersection(list1: List[int], list2: List[int]) -> List[int]:
        """Build the intersection of two lists
        https://www.geeksforgeeks.org/python-intersection-two-lists

        :param list1: A list
        :param list2: A list

        :return: A list of index numbers which appear in both input lists.
        :rtype: list
        """
        intersection = [value for value in list1 if value in list2]
        if len(intersection) > 1:
            intersection = sorted(intersection)
        return intersection

    def _store_index_number(self, attribute_name: str, value: str, index: int) -> None:
        """Add the index number of an entry to the index store.

        :param attribute_name: `mark` or `path`
        :param value: The value of the attribute name. For example
          `$HOME/Downloads` for `path` and `downloads` for `mark`
        :param index: The index number of the entry in the list of
          entries.

        :raises ValueError: If `attribute_name` is not `mark` or `path`.
        """
        if attribute_name not in ("mark", "path"):
            raise ValueError("attribute_name “{}” unkown.".format(attribute_name))
        attribute_index_name = attribute_name + "s"
        if value not in self._index[attribute_index_name]:
            self._index[attribute_index_name][value] = [index]
        elif index not in self._index[attribute_index_name][value]:
            self._index[attribute_index_name][value].append(index)
            self._index[attribute_index_name][value].sort()

    def _update_index(self) -> None:
        """Update the index numbers. Wipe out the whole index, store and
        generate it again."""
        self._index = {
            "marks": {},
            "paths": {},
        }
        index = 0
        for entry in self.entries:
            self._store_index_number("mark", entry.mark, index)
            self._store_index_number("path", entry.path, index)
            index += 1

    def _get_indexes(
        self, mark: Optional[str] = None, path: Optional[str] = None
    ) -> list[int]:
        """Get the index of an entry in the list of entries. Select this entry
        by the bookmark name or by path or by both.

        :param mark: The name of the bookmark / shellmark.
        :param path: The path of the bookmark / shellmark.

        :return: A list of index numbers. Index numbers are starting from
          0.
        :rtype: list

        :raises ValueError: If `mark` or `path` didn’t match.
        """
        marks = self._index["marks"]
        paths = self._index["paths"]

        if mark not in marks and path not in paths:
            return []
        if mark and path:
            if marks[mark] != paths[path]:
                raise ValueError(
                    "mark ({}) and path ({}) didn’t match.".format(mark, path)
                )
            return self._list_intersection(marks[mark], paths[path])
        elif mark and mark in marks:
            return marks[mark]
        elif path and path in paths:
            return paths[path]
        return []

    def get_raw(self) -> str:
        """The raw content of the file specified with the `path` attribute.

        :return: The raw content of the file specified with the `path`
          attribute.
        :rtype: string
        """
        with open(self.path, "r") as file_sdirs:
            content = file_sdirs.read()
        return content

    def get_entry_by_index(self, index: int) -> Entry:
        """Get an entry by the index number.

        :param index: The index number of the entry.

        :return: An entry object
        :rtype: Entry
        """
        return self.entries[index]

    def get_entries(
        self, mark: Optional[str] = None, path: Optional[str] = None
    ) -> list[Entry]:
        """Retrieve shellmark entries for the list of entries. The entries are
        selected by the bookmark name (mark) or by the path or by both.

        :param string mark: The name of the bookmark / shellmark.
        :param string path: The path of the bookmark / shellmark.

        :return: A list of shellmark entries.
        :rtype: list
        """

        indexes = self._get_indexes(mark=mark, path=path)
        return [self.entries[index] for index in indexes]

    def add_entry(
        self,
        mark: str = "",
        path: str = "",
        entry_line: str = "",
        avoid_duplicate_marks: bool = False,
        avoid_duplicate_paths: bool = False,
        delete_old_entries: bool = False,
        validate: bool = True,
        silent: bool = True,
    ) -> int | Literal[False]:
        """Add one bookmark / shellmark entry.

        :param mark: The name of the bookmark / shellmark.
        :param path: The path of the bookmark / shellmark.
        :param entry_line: One line in the file ~/.sdirs
          (export DIR_dir1="/dir1").
        :param avoid_duplicate_marks: Avoid duplicate marks
        :param avoid_duplicate_paths: Avoid duplicate paths
        :param delete_old_entries: Delete old entries instead of not
          adding a new entry.
        :param validate: Validate the attributes `mark` and `path`.
          If invalid, raise an exception.
        :param silent: Add no messages to the action summary (.msg).

        :return: False if adding of a new entry is rejected, else the index
          number.
        :rtype: mixed
        """
        if avoid_duplicate_marks and delete_old_entries:
            self.delete_entries(mark=mark)

        if avoid_duplicate_paths and delete_old_entries:
            self.delete_entries(path=path)

        same_mark_entries = self.get_entries(mark=mark)
        same_path_entries = self.get_entries(path=path)

        if (
            (not avoid_duplicate_marks and not avoid_duplicate_paths)
            or (avoid_duplicate_marks and not same_mark_entries)
            or (avoid_duplicate_paths and not same_path_entries)
        ):
            entry = Entry(mark=mark, path=path, entry=entry_line, validate=validate)
            index = len(self.entries)
            self.entries.append(entry)
            self._store_index_number("mark", entry.mark, index)
            self._store_index_number("path", entry.path, index)
            add_action: int = index
            if not silent:
                self.changes.append(
                    {
                        "action": "add",
                        "mark": entry.mark,
                        "path": entry.path,
                    }
                )
            return add_action
        return False

    def update_entries(
        self,
        old_mark: str = "",
        old_path: str = "",
        new_mark: str = "",
        new_path: str = "",
    ) -> None:
        """Update the entries which match the conditions.

        :param old_mark: The name of the old bookmark / shellmark.
        :param old_path: The path of the old bookmark / shellmark.
        :param new_mark: The name of the new bookmark / shellmark.
        :param new_path: The path of the new bookmark / shellmark.
        """
        indexes = self._get_indexes(mark=old_mark, path=old_path)
        for index in indexes:
            entry = self.get_entry_by_index(index)
            if new_mark:
                entry.mark = new_mark
            if new_path:
                entry.path = new_path
        self._update_index()

    def delete_entries(
        self, mark: Optional[str] = None, path: Optional[str] = None
    ) -> bool:
        """Delete entries which match the specified conditions.

        :param mark: The name of the bookmark / shellmark.
        :param path: The path of the bookmark / shellmark.

        :return: True if deletion was successful, False otherwise.
        :rtype: boolean
        """
        indexes = self._get_indexes(mark=mark, path=path)
        # The deletion of an entry affects the index number of subsequent
        # entries.
        indexes.sort(reverse=True)
        delete_action = False
        for index in indexes:
            entry = self.entries[index]
            self.changes.append(
                {
                    "action": "delete",
                    "mark": entry.mark,
                    "path": entry.path,
                }
            )
            del self.entries[index]
            delete_action = True
        self._update_index()
        return delete_action

    def delete_duplicates(self, marks: bool = True, paths: bool = False) -> None:
        """Delete duplicate entries.

        :param marks: Delete duplicate entries with the same
          mark attribute.
        :param paths: Delete duplicate entries with the same
          path attribute.
        """
        # Create a copy of the entries list.
        old_entries = list(self.entries)
        self.entries = []
        self._update_index()
        for entry in old_entries:
            self.add_entry(
                mark=entry.mark,
                path=entry.path,
                validate=False,
                avoid_duplicate_marks=marks,
                avoid_duplicate_paths=paths,
                delete_old_entries=True,
            )

        duplicate_entries = len(old_entries) - len(self.entries)
        if duplicate_entries > 0:
            self.changes.append(
                {"action": "delete_duplicates", "count": duplicate_entries}
            )

    def cleanup(self) -> None:
        """Clean up invalid entries. Readd all entries which are valid."""
        # Create a copy of the entries list.
        old_entries = list(self.entries)
        self.entries = []
        self._update_index()
        for entry in old_entries:
            try:
                self.add_entry(mark=entry.mark, path=entry.path, validate=True)
            except ShellmarksError:
                pass

        cleanup_entries = len(old_entries) - len(self.entries)
        if cleanup_entries > 0:
            self.changes.append({"action": "cleanup", "count": cleanup_entries})

    def sort(
        self, attribute_name: Literal["mark", "path"] = "mark", reverse: bool = False
    ) -> None:
        """Sort the bookmark entries by mark or path.

        :param attribute_name: 'mark' or 'path'
        :param reverse: Reverse the sort.
        """
        self.entries.sort(
            key=lambda entry: getattr(entry, attribute_name), reverse=reverse
        )
        self._update_index()
        self.changes.append(
            {
                "action": "sort",
                "sort_by": attribute_name,
                "reverse": reverse,
            }
        )

    def write(self, new_path: str = "") -> None:
        """Write the bookmark / shellmarks to the disk.

        :param new_path: Path of a different output file then specifed
          by the initialisation of the object.
        """
        if new_path:
            path = new_path
        else:
            path = self.path
        output_file = open(path, "w")
        for entry in self.entries:
            output_file.write(
                entry.to_export_string(replace_home=self.replace_home) + "\n"
            )
        output_file.close()

    def export(self, command: str, query_command: Optional[str]) -> None:
        for entry in self.entries:
            if query_command is not None:
                query = entry.run_command(query_command)
            else:
                query = None
            if query is None:
                result = entry.run_command(command)
                if result is not None:
                    self.__export_commands.append(result)
        if len(self.__export_commands) > 0:
            self.changes.append(
                {"action": "export", "export_commands": self.__export_commands}
            )


class ModuleParams(TypedDict):
    cleanup: bool
    delete_duplicates: bool
    export: Optional[str]
    export_query: Optional[str]
    mark: Optional[str]
    path: Optional[str]
    replace_home: bool
    sdirs: str
    sorted: bool
    state: Literal["present", "absent"]


class OptionalModuleParams(TypedDict, total=False):
    cleanup: bool
    delete_duplicates: bool
    export: Optional[str]
    export_query: Optional[str]
    mark: Optional[str]
    path: Optional[str]
    replace_home: bool
    sdirs: str
    sorted: bool
    state: Literal["present", "absent"]


def main() -> None:
    """Main function which gets called by Ansible."""
    module = AnsibleModule(
        argument_spec=dict(
            cleanup=dict(default=False, type="bool"),
            delete_duplicates=dict(default=False, type="bool"),
            export=dict(type="str"),
            export_query=dict(type="str"),
            mark=dict(aliases=["bookmark"]),
            path=dict(aliases=["src"]),
            replace_home=dict(default=True, type="bool"),
            sdirs=dict(default="~/.sdirs"),
            sorted=dict(default=True, type="bool"),
            state=dict(default="present", choices=["present", "absent"]),
        ),
        supports_check_mode=True,
    )

    params: ModuleParams = cast(ModuleParams, module.params)

    home_dir = pwd.getpwuid(os.getuid()).pw_dir
    params["sdirs"] = Entry.normalize_path(params["sdirs"], home_dir)
    manager = ShellmarkManager(path=params["sdirs"], validate_on_init=False)
    manager.replace_home = params["replace_home"]

    if params["mark"] and params["path"] and params["state"] == "present":
        try:
            manager.add_entry(
                mark=params["mark"],
                path=params["path"],
                avoid_duplicate_marks=True,
                avoid_duplicate_paths=True,
                delete_old_entries=True,
                silent=False,
            )
        except NoPathError as exception:
            module.fail_json(msg=str(exception))
        except MarkInvalidError as exception:
            module.fail_json(msg=str(exception))

    if (params["mark"] or params["path"]) and params["state"] == "absent":
        manager.delete_entries(mark=params["mark"], path=params["path"])

    if params["cleanup"]:
        manager.cleanup()

    if params["delete_duplicates"]:
        manager.delete_duplicates()

    if params["sorted"]:
        manager.sort()

    if params["export"]:
        manager.export(params["export"], params["export_query"])

    if not module.check_mode and manager.changed:
        manager.write()

    if manager.changed and manager.changes:
        module.exit_json(changed=manager.changed, changes=manager.changes)
    else:
        module.exit_json(changed=manager.changed)


if __name__ == "__main__":
    main()

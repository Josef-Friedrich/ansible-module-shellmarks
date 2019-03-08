#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Josef Friedrich <josef@friedrich.rocks>
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

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
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
'''

EXAMPLES = '''
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
'''

from ansible.module_utils.basic import AnsibleModule
import os
import pwd
import re


def get_path(entry):
    match = re.findall(r'export DIR_.*="(.*)"', entry)
    return match[0]


def get_mark(entry):
    match = re.findall(r'export DIR_(.*)=".*"', entry)
    return match[0]


def check_mark(mark):
    regex = re.compile(r'^[0-9a-zA-Z_]+$')
    match = regex.match(str(mark))
    if match:
        return match.group(0) == mark
    else:
        return False


def del_entries(entries, indexes):
    indexes = sorted(indexes, reverse=True)
    for index in indexes:
        del entries[index]


def normalize_path(path, home_dir):
    if path:
        path = re.sub(r'/$', '', path)
        path = re.sub(r'^~', home_dir, path)
        path = re.sub(r'^\$HOME', home_dir, path)
    else:
        path = ''
    return path


class Entry:
    """A object representation of one line in the ~/.sdirs file"""

    def __init__(self, path='', mark='', entry=''):
        self.mark = ''
        """The name of the bookmark."""

        self.path = ''
        """The path which should be bookmark."""

        if entry and (path or mark):
            raise ValueError('Specify entry OR both path and mark.')

        if (path and not mark) or (mark and not path):
            raise ValueError('Specify both variables: path and mark')

        if entry:
            match = self.parse_entry(entry)
            self.mark = match[0]
            self.path = match[1]
        else:
            self.mark = mark
            self.path = path

        if not check_mark(self.mark):
            raise ValueError('Allowed characters for mark: 0-9a-zA-Z_')

        self.path = self.normalize_path(self.path)

        if not os.path.exists(self.path):
            raise ValueError('Path “{}” doesn’t exist.'.format(self.path))

    def parse_entry(self, entry):
        return re.findall(r'export DIR_(.*)="(.*)"', entry)[0]

    def check_mark(self, mark):
        regex = re.compile(r'^[0-9a-zA-Z_]+$')
        match = regex.match(str(mark))
        if match:
            return match.group(0) == mark
        else:
            return False

    def normalize_path(self, path):
        """Replace ~ and $HOME with a the actual path string. Replace trailing
        slashes. Convert to a absolute path.
        """
        path = re.sub(r'/$', '', path)
        home_dir = pwd.getpwuid(os.getuid()).pw_dir
        path = re.sub(r'^~', home_dir, path)
        path = re.sub(r'^\$HOME', home_dir, path)
        return os.path.abspath(path)

    def to_export_string(self):
        return 'export DIR_{}=\"{}\"'.format(self.mark, self.path)


class ShellmarkEntries:

    def __init__(self, path):

        self.path = path
        """The path of the .sdirs file."""

        self.entries = []
        """A list of shellmark entries. """

        self._marks = {}
        """A dictonary: The key is the bookmark name, the value is the
        the corresponding index number of the self.entries list containing
        entries.
        """

        self._paths = {}
        """A dictonary: The key is the path, the value is the
        the corresponding index number of the self.entries list containing
        entries.
        """

        if os.path.isfile(path):
            sdirs = open(self.path, 'r')
            lines = sdirs.readlines()
            sdirs.close()
        else:
            lines = []

        for line in lines:
            self.add(entry=line)

    def add(self, mark='', path='', entry=''):
        entry = Entry(mark=mark, path=path, entry=entry)
        if entry.mark not in self._marks and entry.path not in self._paths:
            index = len(self.entries)
            self.entries.append(entry)
            self._marks[entry.mark] = index
            self._paths[entry.path] = index

    def update(self, old_mark='', old_path='', new_mark='', new_path=''):
        pass

    def delete(self, mark='', path=''):
        pass

    def write(self, new_path=''):
        pass


class ShellMarks:

    def __init__(self, params, check_mode=False):
        self.check_mode = check_mode
        self.home_dir = pwd.getpwuid(os.getuid()).pw_dir

        defaults = {
            'changed': False,
            'cleanup': False,
            'mark': '',
            'path': '',
            'replace_home': True,
            'sdirs': '~/.sdirs',
            'skipped': False,
            'error': False,
            'sorted': True,
            'state': 'present',
        }
        processed_params = defaults.copy()
        processed_params.update(params)
        for key, value in list(processed_params.items()):
            setattr(self, key, value)

        self.path = normalize_path(self.path, self.home_dir)
        if self.mark:
            self.error = not check_mark(self.mark)

        if self.sdirs == '~/.sdirs':
            self.sdirs = os.path.join(self.home_dir, '.sdirs')

        self.entries = []
        """A list of lines from the file ~/.sdirs.

        One entry (one line) looks like this example.

        export DIR_shellmarks="$HOME/ansible-module-shellmarks"

        """
        self.readSdirs()
        self.entriesOrigin = list(self.entries)
        """A unmodified copy of the attribute self.entries."""

        self.process()

    def readSdirs(self):
        if os.path.isfile(self.sdirs):
            f = open(self.sdirs, 'r')
            self.entries = f.readlines()
            f.close()
        else:
            self.entries = []

    def generateEntry(self):
        path = self.path
        if path and self.mark:
            if self.replace_home:
                path = path.replace(self.home_dir, '$HOME')
            self.entry = 'export DIR_' + self.mark + '=\"' + path + '\"\n'
        else:
            self.entry = False

        return self.entry

    def markSearchPattern(self, mark):
        return 'export DIR_' + mark + '=\"'

    def addEntry(self):
        if self.mark and \
                not self.error and \
                self.path and \
                (os.path.exists(self.path) and self.state == 'present') and \
                self.entry not in self.entries and \
                not [s for s in self.entries if
                     self.markSearchPattern(self.mark) in s]:
            self.entries.append(self.entry)

    def deleteEntry(self):
        if self.mark and not self.path:
            deletions = []
            for index, entry in enumerate(self.entries):
                if self.markSearchPattern(self.mark) in entry:
                    deletions.append(index)
            del_entries(self.entries, deletions)

        elif self.path and not self.mark:
            deletions = []
            for index, entry in enumerate(self.entries):
                if self.path in entry:
                    deletions.append(index)
            del_entries(self.entries, deletions)

        elif self.path and self.mark:
            deletions = []
            for index, entry in enumerate(self.entries):
                if self.entry in entry:
                    deletions.append(index)
            del_entries(self.entries, deletions)

    def cleanUpEntries(self):
        deletions = []
        for index, entry in enumerate(self.entries):
            path = get_path(entry)
            path = path.replace('$HOME', self.home_dir)
            if not os.path.exists(path):
                deletions.append(index)

        del_entries(self.entries, deletions)

    def sort(self):
        self.entries.sort()

    def replaceHome(self):
        self.entries = [entry.replace(self.home_dir, '$HOME')
                        for entry in self.entries]

    def writeSdirs(self):
        f = open(self.sdirs, 'w')
        for entry in self.entries:
            f.write(entry)
        f.close()

    def generateMsg(self):
        if self.skipped and self.path:
            self.msg = "Specifed path (%s) doesn't exist!" % self.path
        elif self.path and self.mark:
            self.msg = self.mark + ' : ' + self.path
        elif self.path:
            self.msg = self.path
        elif self.mark:
            self.msg = self.mark
        else:
            self.msg = ''

    def processSkipped(self):
        if self.path and \
                not os.path.exists(self.path) and \
                self.mark and self.state == 'present':
            self.skipped = True

    def process(self):
        self.generateEntry()
        if self.state == 'present':
            self.addEntry()

        if self.state == 'absent':
            self.deleteEntry()

        if self.replace_home:
            self.replaceHome()

        if self.sorted:
            self.sort()

        if self.cleanup:
            self.cleanUpEntries()

        if self.entries != self.entriesOrigin:
            self.changed = True

        self.processSkipped()

        if not self.check_mode and self.changed:
            self.writeSdirs()

        self.generateMsg()


def mark_entry(bookmark, path):
    for ch in ['-', ' ', '/']:
        if ch in bookmark:
            bookmark = bookmark.replace(ch, '')
    return 'export DIR_' + bookmark + '=\"' + path + '\"\n'


def main():
    module = AnsibleModule(
        argument_spec=dict(
            cleanup=dict(default=False, type='bool'),
            mark=dict(aliases=['bookmark']),
            path=dict(aliases=['src']),
            replace_home=dict(default=True, type='bool'),
            sdirs=dict(default='~/.sdirs'),
            sorted=dict(default=True, type='bool'),
            state=dict(default='present', choices=['present', 'absent']),
        ),
        supports_check_mode=True
    )

    sm = ShellMarks(module.params, module.check_mode)

    if sm.error:
        module.fail_json(msg="Possible characters for mark are: a-z A-Z 0-9 _")

    if sm.skipped:
        module.exit_json(skipped=True, msg=sm.msg)

    module.exit_json(changed=sm.changed, msg=sm.msg)


if __name__ == '__main__':
    main()

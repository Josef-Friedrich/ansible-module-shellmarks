#!/usr/bin/python

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


def normalize_mark(mark):
    if mark:
        for char in ['-', ' ', '/']:
            if char in mark:
                mark = mark.replace(char, '')
    else:
        mark = ''
    return mark


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
            'sorted': True,
            'state': 'present',
        }
        processed_params = defaults.copy()
        processed_params.update(params)
        for key, value in processed_params.items():
            setattr(self, key, value)

        self.path = normalize_path(self.path, self.home_dir)
        self.mark = normalize_mark(self.mark)

        if self.sdirs == '~/.sdirs':
            self.sdirs = os.path.join(self.home_dir, '.sdirs')

        self.readSdirs()
        self.entriesOrigin = list(self.entries)
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
            self.msg = u"Specifed path (%s) doesn't exist!" % self.path
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

    if sm.skipped:
        module.exit_json(skipped=True, msg=sm.msg)

    module.exit_json(changed=sm.changed, msg=sm.msg)


if __name__ == '__main__':
    main()

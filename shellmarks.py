#! /usr/bin/python

# -*- coding: utf-8 -*-

# https://gist.github.com/Josef-Friedrich/7166f86b7d32c65c40532244cb69ccff

# MIT License
#
# Copyright (c) 2017 Josef Friedrich <josef@friedrich.rocks>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from ansible.module_utils.basic import AnsibleModule
import os
import pwd
import re

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: shellmarks
short_description: Mark directories like the tools shellmarks / bashmarks
description:
    - shellmarks U(https://github.com/Bilalh/shellmarks) bashmarks
      U(https://github.com/huyng/bashmarks) are shell script that allows
      you to save and jump to commonly used directories with tab
      completion.

version_added: "1.0"
author: "Josef Friedrich (@Josef-Friedrich)"
options:
    mark:
        description:
            - Name of the bookmark.
        required: true
        default: []
        choices: []
        aliases:
            - bookmark
        version_added: "1.0"
    path:
        description:
            - Full path to the directory to be marked.
        required: true
        default: []
        choices: []
        aliases:
            - src
        version_added: "1.0"
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
        version_added: "1.0"
notes: []
requirements: []
'''

EXAMPLES = '''
# Marks the ansible configuration directory
- shellmarks:
    mark: ansible
    path: /etc/ansible
    state: present
# Unmarks the ansible configuration directory
- shellmarks:
    mark: ansible
    path: /etc/ansible
    state: absent
'''


class ShellMarks:

    def __init__(self, params, check_mode=False):
        self.changed = False
        self.skipped = False
        self.check_mode = check_mode
        self.home_dir = pwd.getpwuid(os.getuid()).pw_dir

        # params
        # mark
        if 'mark' in params:
            self.mark = params['mark']
        else:
            self.mark = False
        # path
        if 'path' in params:
            self.path = params['path']
        else:
            self.path = False
        # replace_home
        if 'replace_home' in params:
            self.replace_home = params['replace_home']
        else:
            self.replace_home = True
        # sdirs
        if 'sdirs' in params:
            self.sdirs = params['sdirs']
        else:
            self.sdirs = '~/.sdirs'
        if self.sdirs == '~/.sdirs':
            self.sdirs = os.path.join(self.home_dir, '.sdirs')
        # sorted
        if 'sorted' in params:
            self.sorted = params['sorted']
        else:
            self.sorted = True
        # state
        if 'state' in params:
            self.state = params['state']
        else:
            self.state = 'present'

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
        if self.path and self.mark:
            for ch in ['-', ' ', '/']:
                if ch in self.mark:
                    self.mark = self.mark.replace(ch, '')
            self.path = re.sub('/$', '', self.path)
            self.path = self.path.replace(self.home_dir, '$HOME')
            self.entry = 'export DIR_' + self.mark + '=\"' + self.path + '\"\n'
        else:
            self.entry = False

        return self.entry

    def addEntry(self):
        if self.mark and \
                self.path and \
                not self.skipped and \
                self.entry not in self.entries and \
                not [s for s in self.entries if
                     'export DIR_' + self.mark + '=\"' in s]:
            self.entries.append(self.entry)

    def deleteEntry(self):
        if self.mark:
            deletions = []
            for index, entry in enumerate(self.entries):
                if 'export DIR_' + self.mark + '=\"' in entry:
                    deletions.append(index)

            for index in deletions:
                del self.entries[index]

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

    def process(self):

        if not os.path.exists(str(self.path)) and self.state == 'present':
            self.skipped = True

        self.generateEntry()
        if self.state == 'present':
            self.addEntry()

        if self.state == 'absent':
            self.deleteEntry()

        if self.replace_home:
            self.replaceHome()

        if self.sorted:
            self.sort()

        if self.entries != self.entriesOrigin:
            self.changed = True

        if not self.check_mode and self.changed:
            self.writeSdirs()

        self.generateMsg()


def mark_entry(bookmark, path):
    for ch in ['-', ' ', '/']:
        if ch in bookmark:
            bookmark = bookmark.replace(ch, '')
    path = re.sub('/$', '', path)
    return 'export DIR_' + bookmark + '=\"' + path + '\"\n'


def main():
    module = AnsibleModule(
        argument_spec=dict(
            mark=dict(required=True, aliases=['bookmark']),
            path=dict(required=True, aliases=['src']),
            replace_home=dict(default=True, type='bool'),
            sdirs=dict(default='~/.sdirs'),
            sorted=dict(default=True, type='bool'),
            state=dict(default='present', choices=['present', 'absent']),
        ),
        supports_check_mode=True
    )

    sm = ShellMarks(module.params, module.check_mode)
    sm.process()

    if sm.skipped:
        module.exit_json(skipped=True, msg=sm.msg)

    module.exit_json(changed=sm.changed, msg=sm.msg)


if __name__ == '__main__':
    main()

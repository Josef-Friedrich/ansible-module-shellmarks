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
            state=dict(default='present', choices=['present', 'absent']),
            sdirs=dict(default='~/.sdirs'),
        ),
        supports_check_mode=True
    )
    p = module.params

    home_dir = pwd.getpwuid(os.getuid()).pw_dir
    if p['sdirs'] == '~/.sdirs':
        sdirs = os.path.join(home_dir, '.sdirs')
    else:
        sdirs = p['sdirs']

    p['path'] = p['path'].replace('$HOME', home_dir)

    if not os.path.exists(p['path']) and p['state'] == 'present':
        module.exit_json(skipped=True,
                         msg=u"Specifed path (%s) doesn't exist!"
                         % p['path'])

    if os.path.isfile(sdirs):
        f = open(sdirs, 'r')
        lines = f.readlines()
        f.close()
    else:
        lines = []

    entry = mark_entry(p['mark'], p['path'])
    entry = entry.replace(home_dir, '$HOME')
    changed = False
    if p['state'] == 'present':
        if entry not in lines:
            lines.append(entry)
            changed = True

    if p['state'] == 'absent':
        if entry in lines:
            lines.remove(entry)
            changed = True

    if changed and not module.check_mode:
        lines.sort()
        lines = [line.replace(home_dir, '$HOME') for line in lines]

        f = open(sdirs, 'w')
        for line in lines:
            f.write(line)
        f.close()

    module.exit_json(changed=changed,
                     msg=p['state'] + ' : ' + p['path'])


if __name__ == '__main__':
    main()

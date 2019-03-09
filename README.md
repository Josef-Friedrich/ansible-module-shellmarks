[![Build Status](https://travis-ci.org/Josef-Friedrich/ansible-module-shellmarks.svg?branch=master)](https://travis-ci.org/Josef-Friedrich/ansible-module-shellmarks)

# ansible-module-shellmarks

`ansible-module-shellmarks` is a [ansible](https://www.ansible.com)
module to set bookmarks to commonly used directories like the tools
[shellmarks](https://github.com/Bilalh/shellmarks) /
[bashmarks](https://github.com/huyng/bashmarks) do.

[shellmarks](https://github.com/Bilalh/shellmarks) and
[bashmarks](https://github.com/huyng/bashmarks) are shell scripts that
allows you to save and jump to commonly used directories with tab
completion.

Both tools store their bookmarks in a text file called `~/.sdirs`. This
module is able to write bookmarks to this file.

```
export DIR_shell_scripts_SHELL_GITHUB="$HOME/shell-scripts"
export DIR_shellmarks_module_ansible="$HOME/ansible-module-shellmarks"
export DIR_skeleton_SHELL_GITHUB="$HOME/skeleton.sh"
```

```
> SHELLMARKS    (shellmarks.py)

  shellmarks https://github.com/Bilalh/shellmarks bashmarks https://github.com/huyng/bashmarks
  are shell scripts that allows you to save and jump to commonly used directories with tab
  completion.

Options (= is mandatory):

- cleanup
        Delete bookmarks of nonexistent directories.
        [Default: False]
- mark
        Name of the bookmark.
        [Default: (null)]
- path
        Full path to the directory.
        [Default: (null)]
- replace_home
        Replace home directory with $HOME variable.
        [Default: True]
- sdirs
        The path to the file where the bookmarks are stored.
        [Default: ~/.sdirs]
- sorted
        Sort entries in the bookmark file.
        [Default: True]
- state
        State of the mark.
        (Choices: present, absent)[Default: present]
EXAMPLES:
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


MAINTAINERS: Josef Friedrich (@Josef-Friedrich)

METADATA:
	Status: ['preview']
	Supported_by: community
```

# Development

## Test functionality

```
/usr/local/src/ansible/hacking/test-module -m shellmarks.py -a
```

## Test documentation

```
source /usr/local/src/ansible/hacking/env-setup
/usr/local/src/ansible/test/sanity/validate-modules/validate-modules --arg-spec --warnings shellmarks.py
```

## Generate documentation

```
ansible-doc -M . shellmarks
```

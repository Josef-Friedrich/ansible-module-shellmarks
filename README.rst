[![Build Status](https://travis-ci.org/Josef-Friedrich/ansible-module-shellmarks.svg?branch=master)](https://travis-ci.org/Josef-Friedrich/ansible-module-shellmarks)
[![Documentation Status](https://readthedocs.org/projects/ansible-module-shellmarks/badge/?version=latest)](https://ansible-module-shellmarks.readthedocs.io/en/latest/?badge=latest)

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


.. code-block:: 

    > GITUPDATER    (/etc/ansible/library/gitupdater.py)

            gitup https://github.com/earwig/git-repo-updater is a console
            script that allows you to easily update multiple git
            repositories at once.

    ADDED IN: version 1.0

    OPTIONS (= is mandatory):

    - cleanup
            Clean up the repositories that have been deleted.
            [Default: False]

    - path
            Full path to the git repository.
            [Default: False]

    - state
            State of the gitup configuration for this repository. The git
            repository itself is not affected.
            (Choices: present, absent)[Default: present]


    REQUIREMENTS:  git-repo-updater

    AUTHOR: Josef Friedrich (@Josef-Friedrich)

    METADATA:
      metadata_version: '1.0'
      status:
      - preview
      supported_by: community


    EXAMPLES:

    # Bookmark a repository, state can be omitted
    - gitupdater:
        path: /var/repos/project

    # Bookmark a repository
    - gitupdater:
        path: /var/repos/project
        state: present

    # Delete bookmark
    - gitupdater:
        path: /var/repos/project
        state: absent

    # Delete non-existent repositories
    - gitupdater:
        cleanup: true


    RETURN VALUES:
    - path
            Full path to the git repository

            returned: always
            sample: /path/to/repository
            type: string

    - state
            State of the gitup configuration for this repository

            returned: always
            sample: present
            type: string



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
|Build Status| |Documentation Status|

ansible-module-shellmarks
=========================

``ansible-module-shellmarks`` is a `ansible <https://www.ansible.com>`__
module to set bookmarks to commonly used directories like the tools
`shellmarks <https://github.com/Bilalh/shellmarks>`__ /
`bashmarks <https://github.com/huyng/bashmarks>`__ do.

`shellmarks <https://github.com/Bilalh/shellmarks>`__ and
`bashmarks <https://github.com/huyng/bashmarks>`__ are shell scripts
that allows you to save and jump to commonly used directories with tab
completion.

Both tools store their bookmarks in a text file called ``~/.sdirs``.
This module is able to write bookmarks to this file.

::

   export DIR_shell_scripts_SHELL_GITHUB="$HOME/shell-scripts"
   export DIR_shellmarks_module_ansible="$HOME/ansible-module-shellmarks"
   export DIR_skeleton_SHELL_GITHUB="$HOME/skeleton.sh"


.. code-block:: 

    > SHELLMARKS    (/etc/ansible/library/shellmarks.py)

            shellmarks https://github.com/Bilalh/shellmarks bashmarks
            https://github.com/huyng/bashmarks are shell scripts that
            allows you to save and jump to commonly used directories with
            tab completion.

    OPTIONS (= is mandatory):

    - cleanup
            Delete bookmarks of nonexistent directories.
            [Default: False]

    - delete_duplicates
            Delete duplicate bookmark entries. This option deletes both
            duplicate mark and duplicate path entries. Entries at the
            beginning are deleted, entries at the end are perserved.
            [Default: False]

    - mark
            Name of the bookmark.
            (Aliases: bookmark)[Default: (null)]

    - path
            Full path to the directory.
            (Aliases: src)[Default: (null)]

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
            (Aliases: src)(Choices: present, absent)[Default: present]


    AUTHOR: Josef Friedrich (@Josef-Friedrich)

    METADATA:
      metadata_version: '1.0'
      status:
      - preview
      supported_by: community


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


    RETURN VALUES:
    - changes
            A list of actions

            returned: On changed
            sample:
            - action: add
              mark: dir1
              path: /dir1
            - action: delete
              mark: dir1
              path: /dir1
            - action: sort
              reverse: false
              sort_by: mark
            - action: cleanup
              count: 1
            
            type: list



Development
===========

Test functionality
------------------

::

   /usr/local/src/ansible/hacking/test-module -m shellmarks.py -a

Test documentation
------------------

::

   source /usr/local/src/ansible/hacking/env-setup
   /usr/local/src/ansible/test/sanity/validate-modules/validate-modules --arg-spec --warnings shellmarks.py

Generate documentation
----------------------

::

   ansible-doc -M . shellmarks

.. |Build Status| image:: https://travis-ci.org/Josef-Friedrich/ansible-module-shellmarks.svg?branch=master
   :target: https://travis-ci.org/Josef-Friedrich/ansible-module-shellmarks
.. |Documentation Status| image:: https://readthedocs.org/projects/ansible-module-shellmarks/badge/?version=latest
   :target: https://ansible-module-shellmarks.readthedocs.io/en/latest/?badge=latest
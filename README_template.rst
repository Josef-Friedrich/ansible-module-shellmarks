{{ badge.pypi }}
{{ badge.github_workflow() }}

ansible-module-shellmarks
=========================

``ansible-module-shellmarks`` is a `ansible <https://www.ansible.com>`_
module to set bookmarks to commonly used directories like the tools
`shellmarks <https://github.com/Bilalh/shellmarks>`_ /
`bashmarks <https://github.com/huyng/bashmarks>`_ do.

`shellmarks <https://github.com/Bilalh/shellmarks>`_ and
`bashmarks <https://github.com/huyng/bashmarks>`_ are shell scripts
that allows you to save and jump to commonly used directories with tab
completion.

Both tools store their bookmarks in a text file called ``~/.sdirs``.
This module is able to write bookmarks to this file.

::

   export DIR_shell_scripts_SHELL_GITHUB="$HOME/shell-scripts"
   export DIR_shellmarks_module_ansible="$HOME/ansible-module-shellmarks"
   export DIR_skeleton_SHELL_GITHUB="$HOME/skeleton.sh"

{{ cli('ansible-doc shellmarks') | code }}

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

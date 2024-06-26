"""
https://github.com/Josef-Friedrich/ansible-stubs/blob/initial-code/ansible-stubs/module_utils/basic.pyi
"""

from typing import Any, NoReturn, Sequence

__metaclass__ = type
FILE_ATTRIBUTES = ...
HAVE_SELINUX = ...
NoneType = ...
AVAILABLE_HASH_ALGORITHMS = ...
SEQUENCETYPE = ...
PASSWORD_MATCH = ...
imap = ...
_literal_eval = ...
_ANSIBLE_ARGS = ...
FILE_COMMON_ARGUMENTS = ...
PASSWD_ARG_RE = ...
MODE_OPERATOR_RE = ...
USERS_RE = ...
PERMS_RE = ...
_PY3_MIN = ...
_PY2_MIN = ...
_PY_MIN = ...

def get_platform() -> str:
    """
    **Deprecated** Use :py:func:`platform.system` directly.

    :returns: Name of the platform the module is running on in a native string

    Returns a native string that labels the platform ("Linux", "Solaris", etc). Currently, this is
    the result of calling :py:func:`platform.system`.
    """
    ...

def load_platform_subclass(cls, *args, **kwargs):
    """**Deprecated**: Use ansible.module_utils.common.sys_info.get_platform_subclass instead"""
    ...

def get_all_subclasses(cls):  # -> list[Unknown]:
    """**Deprecated**: Use ansible.module_utils.common._utils.get_all_subclasses instead"""
    ...

def heuristic_log_sanitize(data, no_log_values=...):
    """Remove strings that look like passwords from log messages"""
    ...

def missing_required_lib(library, reason=..., url=...): ...

class AnsibleModule:
    params: dict[str, Any]

    check_mode: bool

    def __init__(
        self,
        argument_spec,
        bypass_checks=...,
        no_log: bool=...,
        mutually_exclusive: Sequence[Sequence[str]] = ...,
        required_together: Sequence[Sequence[str]] =...,
        required_one_of: Sequence[Sequence[str]] =...,
        add_file_common_args=...,
        supports_check_mode: bool = ...,
        required_if=...,
        required_by=...,
    ) -> None:
        """
        Common code for quickly building an ansible module in Python
        (although you can write modules with anything that can return JSON).

        See :ref:`developing_modules_general` for a general introduction
        and :ref:`developing_program_flow_modules` for more detailed explanation.
        """
        ...

    @property
    def tmpdir(self) -> str: ...
    def warn(self, warning: str) -> None: ...
    def deprecate(self, msg, version=..., date=..., collection_name=...) -> None: ...
    def load_file_common_arguments(self, params, path=...):
        """
        many modules deal with files, this encapsulates common
        options that the file module accepts such that it is directly
        available to all modules and they can share code.

        Allows to overwrite the path/dest module argument by providing path.
        """
        ...
    def selinux_mls_enabled(self) -> bool: ...
    def selinux_enabled(self) -> bool: ...
    def selinux_initial_context(self): ...
    def selinux_default_context(self, path: str, mode: int=...): ...
    def selinux_context(self, path: str): ...
    def user_and_group(self, path: str, expand: bool=...) -> tuple[int, int]: ...
    def find_mount_point(self, path: str) -> str:
        """
            Takes a path and returns it's mount point

        :param path: a string type with a filesystem path
        :returns: the path to the mount point as a text type
        """
        ...
    def is_special_selinux_path(self, path: str):
        """
        Returns a tuple containing (True, selinux_context) if the given path is on a
        NFS or other 'special' fs  mount point, otherwise the return will be (False, None).
        """
        ...
    def set_default_selinux_context(self, path: str, changed): ...
    def set_context_if_different(self, path: str, context, changed, diff=...): ...
    def set_owner_if_different(self, path: str, owner, changed, diff=..., expand: bool=...): ...
    def set_group_if_different(self, path: str, group, changed, diff=..., expand: bool=...): ...
    def set_mode_if_different(self, path: str, mode, changed, diff=..., expand: bool=...): ...
    def set_attributes_if_different(
        self, path: str, attributes, changed, diff=..., expand=...
    ): ...
    def get_file_attributes(self, path: str, include_version=...): ...
    def set_fs_attributes_if_different(
        self, file_args, changed, diff=..., expand: bool=...
    ): ...
    def check_file_absent_if_check_mode(self, file_path: str): ...
    def set_directory_attributes_if_different(
        self, file_args, changed, diff=..., expand: bool=...
    ): ...
    def set_file_attributes_if_different(
        self, file_args, changed, diff=..., expand: bool=...
    ): ...
    def add_path_info(self, kwargs):
        """
        for results that are files, supplement the info about the file
        in the return path with stats about the file path.
        """
        ...
    def safe_eval(self, value, locals=..., include_exceptions=...): ...
    def debug(self, msg): ...
    def log(self, msg, log_args=...): ...
    def get_bin_path(self, arg, required=..., opt_dirs=...):  # -> None:
        """
        Find system executable in PATH.

        :param arg: The executable to find.
        :param required: if executable is not found and required is ``True``, fail_json
        :param opt_dirs: optional list of directories to search in addition to ``PATH``
        :returns: if found return full path; otherwise return None
        """
        ...
    def boolean(self, arg):  # -> bool:
        """Convert the argument to a boolean"""
        ...
    def jsonify(self, data): ...
    def from_json(self, data): ...
    def add_cleanup_file(self, path): ...
    def do_cleanup_files(self): ...
    def exit_json(self, **kwargs: Any) -> NoReturn:
        """return from the module, without error"""
        ...
    def fail_json(self, msg: str, **kwargs: Any) -> NoReturn:
        """return from the module, with an error message"""
        ...
    def fail_on_missing_params(self, required_params=...): ...
    def digest_from_file(self, filename, algorithm):  # -> None:
        """Return hex digest of local file for a digest_method specified by name, or None if file is not present."""
        ...
    def md5(self, filename):  # -> None:
        """Return MD5 hex digest of local file using digest_from_file().

        Do not use this function unless you have no other choice for:
            1) Optional backwards compatibility
            2) Compatibility with a third party protocol

        This function will not work on systems complying with FIPS-140-2.

        Most uses of this function can use the module.sha1 function instead.
        """
        ...
    def sha1(self, filename):  # -> None:
        """Return SHA1 hex digest of local file using digest_from_file()."""
        ...
    def sha256(self, filename):  # -> None:
        """Return SHA-256 hex digest of local file using digest_from_file()."""
        ...
    def backup_local(self, fn):  # -> str:
        """make a date-marked backup of the specified file, return True or False on success or failure"""
        ...
    def cleanup(self, tmpfile): ...
    def preserved_copy(self, src, dest):
        """Copy a file with preserved ownership, permissions and context"""
        ...
    def atomic_move(self, src, dest, unsafe_writes=...):
        """atomically move src to dest, copying attributes from dest, returns true on success
        it uses os.rename to ensure this as it is an atomic operation, rest of the function is
        to work around limitations, corner cases and ensure selinux context is saved if possible"""
        ...
    def run_command(
        self,
        args,
        check_rc: bool = ...,
        close_fds: bool = ...,
        executable=...,
        data=...,
        binary_data=...,
        path_prefix=...,
        cwd=...,
        use_unsafe_shell=...,
        prompt_regex=...,
        environ_update=...,
        umask=...,
        encoding=...,
        errors=...,
        expand_user_and_vars=...,
        pass_fds=...,
        before_communicate_callback=...,
        ignore_invalid_cwd=...,
        handle_exceptions=...,
    ):
        """
        Execute a command, returns rc, stdout, and stderr.

        :arg args: is the command to run
            * If args is a list, the command will be run with shell=False.
            * If args is a string and use_unsafe_shell=False it will split args to a list and run with shell=False
            * If args is a string and use_unsafe_shell=True it runs with shell=True.
        :kw check_rc: Whether to call fail_json in case of non zero RC.
            Default False
        :kw close_fds: See documentation for subprocess.Popen(). Default True
        :kw executable: See documentation for subprocess.Popen(). Default None
        :kw data: If given, information to write to the stdin of the command
        :kw binary_data: If False, append a newline to the data.  Default False
        :kw path_prefix: If given, additional path to find the command in.
            This adds to the PATH environment variable so helper commands in
            the same directory can also be found
        :kw cwd: If given, working directory to run the command inside
        :kw use_unsafe_shell: See `args` parameter.  Default False
        :kw prompt_regex: Regex string (not a compiled regex) which can be
            used to detect prompts in the stdout which would otherwise cause
            the execution to hang (especially if no input data is specified)
        :kw environ_update: dictionary to *update* environ variables with
        :kw umask: Umask to be used when running the command. Default None
        :kw encoding: Since we return native strings, on python3 we need to
            know the encoding to use to transform from bytes to text.  If you
            want to always get bytes back, use encoding=None.  The default is
            "utf-8".  This does not affect transformation of strings given as
            args.
        :kw errors: Since we return native strings, on python3 we need to
            transform stdout and stderr from bytes to text.  If the bytes are
            undecodable in the ``encoding`` specified, then use this error
            handler to deal with them.  The default is ``surrogate_or_strict``
            which means that the bytes will be decoded using the
            surrogateescape error handler if available (available on all
            python3 versions we support) otherwise a UnicodeError traceback
            will be raised.  This does not affect transformations of strings
            given as args.
        :kw expand_user_and_vars: When ``use_unsafe_shell=False`` this argument
            dictates whether ``~`` is expanded in paths and environment variables
            are expanded before running the command. When ``True`` a string such as
            ``$SHELL`` will be expanded regardless of escaping. When ``False`` and
            ``use_unsafe_shell=False`` no path or variable expansion will be done.
        :kw pass_fds: When running on Python 3 this argument
            dictates which file descriptors should be passed
            to an underlying ``Popen`` constructor. On Python 2, this will
            set ``close_fds`` to False.
        :kw before_communicate_callback: This function will be called
            after ``Popen`` object will be created
            but before communicating to the process.
            (``Popen`` object will be passed to callback as a first argument)
        :kw ignore_invalid_cwd: This flag indicates whether an invalid ``cwd``
            (non-existent or not a directory) should be ignored or should raise
            an exception.
        :kw handle_exceptions: This flag indicates whether an exception will
            be handled inline and issue a failed_json or if the caller should
            handle it.
        :returns: A 3-tuple of return code (integer), stdout (native string),
            and stderr (native string).  On python2, stdout and stderr are both
            byte strings.  On python3, stdout and stderr are text strings converted
            according to the encoding and errors parameters.  If you want byte
            strings on python3, use encoding=None to turn decoding to text off.
        """
        ...

    def append_to_file(self, filename, str) -> None: ...
    def bytes_to_human(self, size) -> str: ...

    pretty_bytes = ...
    def human_to_bytes(self, number, isbits=...): ...

    is_executable = ...
    def get_buffer_size(fd) -> int: ...

def get_module_path() -> str: ...

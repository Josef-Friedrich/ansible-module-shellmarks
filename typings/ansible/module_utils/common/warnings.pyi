"""
This type stub file was generated by pyright.
"""

__metaclass__ = type
_global_warnings = ...
_global_deprecations = ...

def warn(warning): ...
def deprecate(msg, version=..., date=..., collection_name=...): ...
def get_warning_messages():  # -> tuple[Unknown, ...]:
    """Return a tuple of warning messages accumulated over this run"""
    ...

def get_deprecation_messages():  # -> tuple[Unknown, ...]:
    """Return a tuple of deprecations accumulated over this run"""
    ...
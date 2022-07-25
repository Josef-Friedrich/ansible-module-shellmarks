"""
This type stub file was generated by pyright.
"""

__metaclass__ = type

class ValidationResult:
    """Result of argument spec validation.

    This is the object returned by :func:`ArgumentSpecValidator.validate()
    <ansible.module_utils.common.arg_spec.ArgumentSpecValidator.validate()>`
    containing the validated parameters and any errors.
    """

    def __init__(self, parameters) -> None:
        """
        :arg parameters: Terms to be validated and coerced to the correct type.
        :type parameters: dict
        """
        ...
    @property
    def validated_parameters(self):  # -> Unknown:
        """Validated and coerced parameters."""
        ...
    @property
    def unsupported_parameters(self):  # -> set[Unknown]:
        """:class:`set` of unsupported parameter names."""
        ...
    @property
    def error_messages(self):  # -> list[Unknown]:
        """:class:`list` of all error messages from each exception in :attr:`errors`."""
        ...

class ArgumentSpecValidator:
    """Argument spec validation class

    Creates a validator based on the ``argument_spec`` that can be used to
    validate a number of parameters using the :meth:`validate` method.
    """

    def __init__(
        self,
        argument_spec,
        mutually_exclusive=...,
        required_together=...,
        required_one_of=...,
        required_if=...,
        required_by=...,
    ) -> None:
        """
        :arg argument_spec: Specification of valid parameters and their type. May
            include nested argument specs.
        :type argument_spec: dict[str, dict]

        :kwarg mutually_exclusive: List or list of lists of terms that should not
            be provided together.
        :type mutually_exclusive: list[str] or list[list[str]]

        :kwarg required_together: List of lists of terms that are required together.
        :type required_together: list[list[str]]

        :kwarg required_one_of: List of lists of terms, one of which in each list
            is required.
        :type required_one_of: list[list[str]]

        :kwarg required_if: List of lists of ``[parameter, value, [parameters]]`` where
            one of ``[parameters]`` is required if ``parameter == value``.
        :type required_if: list

        :kwarg required_by: Dictionary of parameter names that contain a list of
            parameters required by each key in the dictionary.
        :type required_by: dict[str, list[str]]
        """
        ...
    def validate(self, parameters, *args, **kwargs):
        """Validate ``parameters`` against argument spec.

        Error messages in the :class:`ValidationResult` may contain no_log values and should be
        sanitized with :func:`~ansible.module_utils.common.parameters.sanitize_keys` before logging or displaying.

        :arg parameters: Parameters to validate against the argument spec
        :type parameters: dict[str, dict]

        :return: :class:`ValidationResult` containing validated parameters.

        :Simple Example:

            .. code-block:: text

                argument_spec = {
                    'name': {'type': 'str'},
                    'age': {'type': 'int'},
                }

                parameters = {
                    'name': 'bo',
                    'age': '42',
                }

                validator = ArgumentSpecValidator(argument_spec)
                result = validator.validate(parameters)

                if result.error_messages:
                    sys.exit("Validation failed: {0}".format(", ".join(result.error_messages))

                valid_params = result.validated_parameters
        """
        ...

class ModuleArgumentSpecValidator(ArgumentSpecValidator):
    """Argument spec validation class used by :class:`AnsibleModule`.

    This is not meant to be used outside of :class:`AnsibleModule`. Use
    :class:`ArgumentSpecValidator` instead.
    """

    def __init__(self, *args, **kwargs) -> None: ...
    def validate(self, parameters): ...

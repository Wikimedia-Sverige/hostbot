"""Module for loading and reading from a config file. For sample
config, see `hb_config.sample.py`.
"""

import imp
import os

config = None


def load_config_module(module_path):
    """Load a config file.

    `module_path` is the path to the file containing the config module.
    """

    module_name = os.path.splitext(os.path.basename(module_path))[0]
    globals()["config"] = imp.load_source(module_name, module_path)


def get(variable):
    """Get the value of a config variable."""

    if not hasattr(config, variable):
        raise Exception(
            "Variable '{}' not found in config file.".format(variable)
        )
    value = getattr(config, variable)
    # If the value is a tuple where the first item is a function, call
    # the function with the remaining items as arguments. The value is
    # set to the return value, so that the function doesn't need to be
    # called if the variable is read again.
    if isinstance(value, tuple) and callable(value[0]):
        function = value[0]
        arguments = value[1:]
        setattr(config, variable, function(*arguments))
    return getattr(config, variable)

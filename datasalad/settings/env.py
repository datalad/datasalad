from __future__ import annotations

import logging
from os import (
    environ,
)
from os import (
    name as os_name,
)
from typing import (
    TYPE_CHECKING,
)

from datasalad.settings.setting import Setting
from datasalad.settings.source import WritableSource

if TYPE_CHECKING:
    from collections.abc import Collection, Hashable

lgr = logging.getLogger('datasalad.settings')


class Environment(WritableSource):
    """Process environment source

    This is a stateless source implementation that gets and sets items directly
    in the process environment.

    Environment variables to be read can be filtered by declaring a name
    prefix. More complex filter rules can be implemented by replacing the
    :meth:`include_var()` method in a subclass.

    It is possible to transform an environment variable name to a setting key
    (and vice versa), by implementing the methods
    :meth:`get_key_from_varname()` and :meth:`get_varname_from_key()`.

    .. attention::

       Due to peculiarities of the behavior of Python's ``os.environ`` on the
       windows platform (and ``os2``), all variable names are converted to
       upper case, and are effectively treated as case-insensitive, on that
       platform. For this default implementation this implies that the
       :meth:`~Environment.keys` method can only ever return uppercase keys.
       Reimplement :meth:`~Environment.get_key_from_varname` to change this.
       Retrieving a value for an individual key will nevertheless work for the
       default implementation even with a lowercase or mixed case key.
    """

    def __init__(
        self,
        *,
        var_prefix: str | None = None,
    ):
        super().__init__()
        self._var_prefix = (
            var_prefix.upper()
            if var_prefix is not None and os_name in ('os2', 'nt')
            else var_prefix
        )

    def _reinit(self):
        """Does nothing"""

    def _load(self) -> None:
        """Does nothing

        All accessors inspect the process environment directly.
        """

    def _get_item(self, key: Hashable) -> Setting:
        return Setting(value=environ[self.get_varname_from_key(key)])

    def _set_item(self, key: Hashable, value: Setting) -> None:
        name = self.get_varname_from_key(key)
        environ[name] = str(value.value)

    def _del_item(self, key: Hashable) -> None:
        name = self.get_varname_from_key(key)
        del environ[name]

    def _get_keys(self) -> Collection:
        """Returns all keys that can be determined from the environment

        .. attention::

           Due to peculiarities of the behavior of Python's ``os.environ`` on
           the windows platform (and ``os2``), this method can only report
           uppercase keys with the default implementation. Reimplement
           :meth:`get_key_from_varname()` to modify this behavior.
        """
        varmap = {
            k: self.get_key_from_varname(k)
            for k, v in environ.items()
            if self.include_var(name=k, value=v)
        }
        _keys = set(varmap.values())
        if len(_keys) < len(varmap):
            allkeys = list(varmap.values())
            lgr.warning(
                'Ambiguous ENV variables map on identical keys: %r',
                {
                    key: [k for k in sorted(varmap) if varmap[k] == key]
                    for key in _keys
                    if allkeys.count(key) > 1
                },
            )
        return _keys

    def __str__(self):
        return f'Environment[{self._var_prefix}]' if self._var_prefix else 'Environment'

    def __contains__(self, key: Hashable) -> bool:
        # we only need to reimplement this due to Python's behavior to
        # forece-modify environment variable names on Windows. Only
        # talking directly for environ accounts for that
        return self.get_varname_from_key(key) in environ

    def __repr__(self):
        # TODO: list keys?
        return 'Environment()'

    def include_var(
        self,
        name: str,
        value: str,  # noqa: ARG002 (default implementation does not need it)
    ) -> bool:
        """Determine whether to source a setting from an environment variable

        This default implementation tests whether the name of the variable
        starts with the ``var_prefix`` given to the constructor.

        Reimplement this method to perform custom tests.
        """
        return name.startswith(self._var_prefix or '')

    def get_key_from_varname(self, name: str) -> Hashable:
        """Transform an environment variable name to a setting key

        This default implementation returns the unchanged name as a key.

        Reimplement this method and ``get_varname_from_key()`` to perform
        custom transformations.
        """
        return name

    def get_varname_from_key(self, key: Hashable) -> str:
        """Transform a setting key to an environment variable name

        This default implementation only checks for illegal names and
        raises a ``ValueError``. Otherwise it returns the unchanged key.

        .. attention::

           Due to peculiarities of the behavior of Python's ``os.environ``
           on the windows platform, all variable names are converted to
           upper case, and are effectively treated as case-insensitive,
           on that platform.
        """
        varname = str(key)
        if '=' in varname or '\0' in varname:
            msg = "illegal environment variable name (contains '=' or NUL)"
            raise ValueError(msg)
        if os_name in ('os2', 'nt'):
            # https://stackoverflow.com/questions/19023238/why-python-uppercases-all-environment-variables-in-windows
            return varname.upper()
        return varname

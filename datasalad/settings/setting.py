from __future__ import annotations

from copy import copy
from typing import (
    Any,
    Callable,
)


class UnsetValue:
    """Placeholder type to indicate a value that has not been set"""


class Setting:
    """Representation of an individual setting"""

    def __init__(
        self,
        value: Any | UnsetValue = UnsetValue,
        *,
        coercer: Callable | None = None,
        lazy: bool = False,
    ):
        """
        ``value`` can be of any type.  A setting instance created with
        default :class:`UnsetValue` represents a setting with no known value.

        The ``coercer`` is a callable that processes a setting value
        on access via :attr:`value`. This callable can perform arbitrary
        processing, including type conversion and validation.

        If ``lazy`` is ``True``, ``value`` must be a callable that requires
        no parameters. This callable will be executed each time :attr:`value`
        is accessed, and its return value is passed to the ``coercer``.
        """
        if lazy and not callable(value):
            msg = 'callable required for lazy evaluation'
            raise ValueError(msg)
        self._value = value
        self._coercer = coercer
        self._lazy = lazy

    @property
    def pristine_value(self) -> Any:
        """Original, uncoerced value"""
        return self._value

    @property
    def value(self) -> Any:
        """Value of a setting after coercion

        For a lazy setting, accessing this property also triggers the
        evaluation.
        """
        # we ignore the type error here
        # "error: "UnsetValue" not callable"
        # because we rule this out in the constructor
        val = self._value() if self._lazy else self._value  # type: ignore [operator]
        if self._coercer:
            return self._coercer(val)
        return val

    @property
    def coercer(self) -> Callable | None:
        """``coercer`` of a setting, or ``None`` if there is none"""
        return self._coercer

    @property
    def is_lazy(self) -> bool:
        """Flag whether the setting evaluates on access"""
        return self._lazy

    def update(self, other: Setting) -> None:
        """Update the item from another

        This replaces any ``value`` or ``coercer`` set in the other
        setting. If case the other's ``value`` is :class:`UnsetValue`
        no update of the ``value`` is made. Likewise, if ``coercer``
        is ``None``, no update is made. Update to or from a ``lazy``
        value will also update the ``lazy`` property accordingly.
        """
        if other._value is not UnsetValue:  # noqa: SLF001
            self._value = other._value  # noqa: SLF001
            # we also need to synchronize the lazy eval flag
            # so we can do the right thing (TM) with the
            # new value
            self._lazy = other._lazy  # noqa: SLF001

        if other._coercer:  # noqa: SLF001
            self._coercer = other._coercer  # noqa: SLF001

    def __str__(self) -> str:
        # wrap the value in the classname to make clear that
        # the actual object type is different from the value
        return f'{self.__class__.__name__}({self._value})'

    def __repr__(self) -> str:
        # wrap the value in the classname to make clear that
        # the actual object type is different from the value
        return (
            f'{self.__class__.__name__}('
            f'{self._value!r}'
            f', coercer={self._coercer!r}'
            f', lazy={self._lazy}'
            ')'
        )

    def __eq__(self, item: object) -> bool:
        """
        This default implementation of comparing for equality only compare the
        types, value, and coercer of the two items. If additional criteria are
        relevant for derived classes :meth:`__eq__` has to be reimplemented.
        """
        if not isinstance(item, type(self)):
            return False
        return (
            self._lazy == item._lazy
            and self._value == item._value
            and self._coercer == item._coercer
        )

    def copy(self):
        """Return a shallow copy of the instance"""
        return copy(self)

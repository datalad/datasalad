from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    TYPE_CHECKING,
    Any,
)

from datasalad.settings.setting import Setting

if TYPE_CHECKING:
    from collections.abc import Collection, Generator, Hashable


class Source(ABC):
    """Abstract base class a settings source.

    This class offers a ``dict``-like interface. Individual settings can be
    retrieved via the standard accessor methods :meth:`~Source.__getitem__`,
    and :meth:`~Source.get`.

    If the underlying source can represent multiple settings under a single
    key, the standard accessors :meth:`Source.__getitem__` and
    :meth:`Source.get` nevertheless return a single
    :class:`~datasalad.settings.Setting` only. It is the decision of the
    source implementation to select the most appropriate setting to return.
    Such multi-value sources should reimplement :meth:`Source._getall`
    to provide access to all values for a given key.

    A number of methods have to be implemented for any concrete source
    (see their documentation for details on the expected behavior):

    - :meth:`Source._reinit` (see :meth:`Source.reinit`)
    - :meth:`Source._load` (see :meth:`Source.load`)
    - :meth:`Source._get_keys` (see :meth:`Source.keys`)
    - :meth:`Source._get_item` (see :meth:`Source.__getitem__`)

    This class is in itself a suitable base for a generic read-only setting
    source. For other scenarios alternative base class are also available:

    - :class:`~datasalad.settings.WritableSource`
    - :class:`~datasalad.settings.WritableMultivalueSource`
    - :class:`~datasalad.settings.CachingSource`
    - :class:`~datasalad.settings.InMemory`
    """

    item_type: type = Setting
    """Type to wrap default value in for :meth:`get()`"""

    def load(self) -> None:
        """Load items from the underlying source.

        This default implementation calls a source's internal `_load()` method.
        It is expected that after calling this method, an instance of this
        source reports on items according to the latest state of the source.

        No side-effects are implied. Particular implementations may
        even choose to have this method be a no-op.

        Importantly, calling this method does not imply a call to
        :meth:`~Source.reinit`. If a from-scratch reload is desired,
        :meth:`~Source.reinit` must be called explicitly.
        """
        self._load()

    def reinit(self) -> Source:
        """Re-initialize source instance

        Re-initializing is resetting any state of the source interface instance
        such that a subsequent :meth:`~Source.load` fully synchronizes the
        reporting of settings with the state of the underlying source. Calling
        this method does *not* imply resetting the underlying settings source
        (e.g., removing all settings from the source).

        This method returns ``self`` for convenient chaining of a ``load()``
        call.
        """
        self._reinit()
        return self

    def __getitem__(self, key: Hashable) -> Setting:
        """Calls a source's internal `_get_item()` method"""
        return self._get_item(key)

    def keys(self) -> Collection:
        """Returns all setting keys known to a source"""
        return self._get_keys()

    @property
    def is_writable(self) -> bool:
        """Flag whether configuration item values can be set at the source

        This default implementation returns ```False``.
        """
        return False

    def get(self, key: Hashable, default: Any = None) -> Setting:
        """Return a particular setting identified by its key, or a default

        This method calls ``__getitem__``, and returns the default on
        a ``KeyError`` exception.

        When the ``default`` value is not given as an instance of
        :class:`~datasalad.settings.Setting`, it will be
        automatically wrapped into the one given by :attr:`Source.item_type`.
        """
        try:
            return self[key]
        except KeyError:
            return self._get_default_setting(default)

    def getall(self, key: Hashable, default: Any = None) -> tuple[Setting, ...]:
        """Return all individual settings registered for a key

        Derived classes for source that can represent multiple values for
        a single key should reimplement the internal accessor :meth:`Source._getall`
        appropriately.
        """
        try:
            return self._getall(key)
        except KeyError:
            return (self._get_default_setting(default),)

    def _getall(self, key: Hashable) -> tuple[Setting, ...]:
        """Returns all settings for a key, or raises ``KeyError``

        This default implementation returns a length-one tuple with the
        return value of :meth:`~Source.get`.
        """
        return (self[key],)

    def __len__(self) -> int:
        return len(self.keys())

    def __contains__(self, key: Hashable) -> bool:
        return key in self.keys()

    def __iter__(self) -> Generator[Hashable]:
        yield from self.keys()

    def _get_default_setting(self, default: Any) -> Setting:
        if isinstance(default, Setting):
            return default
        return self.item_type(value=default)

    @abstractmethod
    def _load(self) -> None:
        """Implement to load settings from the source"""

    @abstractmethod
    def _reinit(self) -> None:
        """Implement to reinitialize the state of the source interface"""

    @abstractmethod
    def _get_keys(self) -> Collection:
        """Implement to return the collection of keys for a source"""

    @abstractmethod
    def _get_item(self, key: Hashable) -> Setting:
        """Implement to return a single item

        Or raise ``KeyError`` if there is none.
        """


class WritableSource(Source):
    """Extends ``Source`` with a setter interface

    By default, the :attr:`is_writable` property of a class instance is
    ``True``.
    """

    @property
    def is_writable(self) -> bool:
        """Flag whether configuration item values can be set at the source

        This default implementation returns ```True``.
        """
        return True

    def __setitem__(self, key: Hashable, value: Setting) -> None:
        """Assign a single (exclusive) setting to the given key"""
        self._ensure_writable()
        self._set_item(key, value)

    def __delitem__(self, key: Hashable):
        """Remove the key and all associated information from the source"""
        self._ensure_writable()
        self._del_item(key)

    def _ensure_writable(self):
        if not self.is_writable:
            msg = 'Source is (presently) not writable'
            raise RuntimeError(msg)

    @abstractmethod
    def _set_item(self, key: Hashable, value: Setting) -> None:
        """Implement to set a value for a key in a source"""

    @abstractmethod
    def _del_item(self, key: Hashable):
        """Implement to remove a key form the source"""


class WritableMultivalueSource(WritableSource):
    def add(self, key: Hashable, value: Setting) -> None:
        """Add a additional setting under a given key

        If the key is not yet known, it will be added, and the given
        setting will become the first assigned value.
        """
        self._ensure_writable()
        self._add(key, value)

    def _add(self, key: Hashable, value: Setting) -> None:
        """Internal method to add a setting to a key

        This default implementation relies on retrieving any existing setting
        values and then reassigning via
        :meth:`WritableMultivalueSource.setall`. Reimplement to support more
        efficient approaches for a given source type.
        """
        if key in self:
            self.setall(key, (*self.getall(key), value))
        else:
            self[key] = value

    def setall(self, key: Hashable, values: tuple[Setting, ...]) -> None:
        """Implement to set all given values in the underlying source"""
        self._ensure_writable()
        self._setall(key, values)

    @abstractmethod
    def _setall(self, key: Hashable, values: tuple[Setting, ...]) -> None:
        """ """


class CachingSource(WritableMultivalueSource):
    """Extends ``WritableSource`` with an in-memory cache

    On first access of any setting the ``reinit()`` and ``load()`` methods of a
    subclass are called.

    On load, an implementation can use the standard ``__setitem__()`` method of
    this class directly to populate the cache. Any subsequent read access is
    reported directly from this cache.

    Subclasses should generally reimplement ``__setitem__()`` to call the base
    class implementation in addition to setting a value in the actual source.
    """

    def __init__(self) -> None:
        super().__init__()
        self.__items: dict[Hashable, Setting | tuple[Setting, ...]] | None = None

    @property
    def _items(self) -> dict[Hashable, Setting | tuple[Setting, ...]]:
        if self.__items is None:
            self.reinit().load()
        if TYPE_CHECKING:
            assert self.__items is not None
        return self.__items

    def _reinit(self) -> None:
        # particular implementations may not use this facility,
        # but it is provided as a convenience. Maybe factor
        # it out into a dedicated subclass even.
        self.__items = {}

    def __len__(self) -> int:
        return len(self._items)

    def _get_item(self, key: Hashable) -> Setting:
        val = self._items[key]
        if isinstance(val, tuple):
            return val[-1]
        return val

    def _set_item(self, key: Hashable, value: Setting) -> None:
        self._items[key] = value

    def _del_item(self, key: Hashable):
        del self._items[key]

    def __contains__(self, key: Hashable) -> bool:
        return key in self._items

    def _get_keys(self) -> Collection[Hashable]:
        return self._items.keys()

    def _setall(self, key: Hashable, values: tuple[Setting, ...]) -> None:
        self._items[key] = values

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._items!r})'

    def __str__(self) -> str:
        return ''.join(
            (
                f'{self.__class__.__name__}(',
                ','.join(
                    # we use the pristine value here to avoid issues
                    # with validation/coercion failures when rendering
                    # sources
                    f'{k}=({",".join(repr(val.pristine_value) for val in v)})'
                    if isinstance(v, tuple)
                    else f'{k}={v.pristine_value!r}'
                    for k, v in self._items.items()
                ),
                ')',
            )
        )

    def _getall(self, key: Hashable) -> tuple[Setting, ...]:
        # ok to let KeyError bubble up
        val = self._items[key]
        if isinstance(val, tuple):
            return val
        return (val,)


class InMemory(CachingSource):
    """Extends ``CachingSource`` with a no-op ``load()`` implementation

    This class provides a directly usable implementation of a setting source
    that manages all settings in memory only, and does not load information
    from any actual source.
    """

    is_writable = True

    def _load(self) -> None:
        """Does nothing

        An instance of :class:`InMemory` has no underlying source
        to load from.
        """

    def __str__(self):
        return f'{self.__class__.__name__}'

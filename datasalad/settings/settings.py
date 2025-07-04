from __future__ import annotations

from copy import copy
from itertools import chain
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
)

from datasalad.settings.setting import Setting

if TYPE_CHECKING:
    from collections.abc import Hashable

    from datasalad.settings import Source


class Settings:
    """Query across different sources of settings

    This class implements key parts of the standard ``dict`` interface
    (with some additions).

    An instance is initialized with an ordered  mapping of source identifiers
    to :class:`~datasalad.settings.Source` instances. The order reflects
    the precedence rule with which settings and their properties are selected
    for reporting across sources. Source declared earlier take precedence over
    sources declared later.

    When an individual setting is requested via the ``__getitem__()`` method, a
    "flattened" representation of the item across all sources is determined and
    returned. This is not necessarily a setting that exists in this exact form
    at any source. Instead, for each setting property the value from the source
    with the highest precedence is looked up and used for the return item.

    In practice, this means that, for example, a ``coercer`` can come from a
    lower-precedence source and the setting's ``value`` from a different
    higher-precedence source.

    See :meth:`~Settings.getall` for an alternative access method.
    """

    item_type: type = Setting
    """Type to wrap default value in for :meth:`get()` and
    :meth:`getall()`."""

    def __init__(
        self,
        sources: dict[str, Source],
    ):
        # we keep the sources strictly separate.
        # the order here matters and represents the
        # precedence rule
        self._sources = sources

    @property
    def sources(self) -> MappingProxyType:
        """Read-only mapping of source identifiers to source instance

        This property is used to select individual sources for source-specific
        operations, such as writing a setting to an underlying source.
        """
        return MappingProxyType(self._sources)

    def __len__(self):
        return len(self.keys())

    def __getitem__(self, key: Hashable) -> Setting:
        """Some"""
        # this will become the return item
        item: Setting | None = None
        # now go from the back
        # - start with the first Setting class instance we get
        # - update a copy of this particular instance with all information
        #   from sources with higher priority and flatten it across
        #   sources
        for s in reversed(self._sources.values()):
            update_item = None
            try:
                update_item = s[key]
            except KeyError:
                # source does not have it, proceed
                continue
            if item is None:
                # in-place modification and destroy the original
                # item's integrity
                item = copy(update_item)
                continue
            # we run the update() method of the first item we ever found.
            # this will practically make the type produced by the lowest
            # precedence source define the behavior. This is typically
            # some kind of implementation default
            item.update(update_item)
        if item is None:
            # there was nothing
            raise KeyError
        return item

    def __contains__(self, key: Hashable):
        return any(key in s for s in self._sources.values())

    def keys(self) -> set[Hashable]:
        """Returns all setting keys known across all sources"""
        return set(chain.from_iterable(s.keys() for s in self._sources.values()))

    def get(self, key: Hashable, default: Any = None) -> Setting:
        """Return a particular setting identified by its key, or a default

        The composition of the returned setting follows the same rules
        as the access via ``__getitem__``.

        When the ``default`` value is not given as an instance of
        :class:`~datasalad.settings.Setting`, it will be
        automatically wrapped into the one given by :attr:`Settings.item_type`.
        """
        try:
            return self[key]
        except KeyError:
            return self._get_default_setting(default)

    def getall(
        self,
        key: Hashable,
        default: Any = None,
    ) -> tuple[Setting, ...]:
        """Returns a tuple of all known setting instances for a key across sources

        If no source has any information for a given key, a length-one tuple
        with a :class:`~datasalad.settings.Setting` instance for the given
        ``default`` value is returned.
        """
        # no flattening, get all from all
        items: tuple[Setting, ...] = ()
        for s in reversed(self._sources.values()):
            if key in s:
                # we checked before, no need to handle a default here
                items = (
                    (*items, *s.getall(key))
                    if hasattr(s, 'getall')
                    else (*items, s[key])
                )
        return items if items else (self._get_default_setting(default),)

    def _get_default_setting(self, default: Any) -> Setting:
        if isinstance(default, Setting):
            return default
        return self.item_type(value=default)

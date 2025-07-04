from __future__ import annotations

import logging
from typing import (
    TYPE_CHECKING,
)

from datasalad.settings.source import InMemory

if TYPE_CHECKING:
    from collections.abc import Hashable

    from datasalad.settings.setting import Setting

lgr = logging.getLogger('datasalad.settings')


class Defaults(InMemory):
    """Source for collecting implementation defaults of settings

    Such defaults are not loaded from any source. Clients have to set any items
    they want to see a default be known for. There would typically be only one
    instance of this class, and it would then be the true source of this
    information by itself.

    The difference to :class:`InMemory` is minimal. It is limited
    to emitting a debug-level log message when setting the value of an item
    that has already been set before.

    >>> from datasalad.settings import Defaults, InMemory, Setting, Settings
    >>> defaults = Defaults()
    >>> defaults['myswitch'] = Setting(
    ...     'on', coercer=lambda x: {'on': True, 'off': False}[x]
    ... )
    >>> defaults['myswitch'].value
    True
    >>> settings = Settings({'overrides': InMemory(), 'defaults': defaults})
    >>> settings['myswitch'].value
    True
    >>> settings.sources['overrides']['myswitch'] = Setting('off')
    >>> settings['myswitch'].value
    False
    >>> settings.sources['overrides']['myswitch'] = Setting('broken')
    >>> settings['myswitch'].value
    Traceback (most recent call last):
    KeyError: 'broken'
    """

    def _set_item(self, key: Hashable, value: Setting) -> None:
        if key in self:
            # resetting is something that is an unusual event.
            # __setitem__ does not allow for a dedicated "force" flag,
            # so we leave a message at least
            lgr.debug('Resetting %r default', key)
        super()._set_item(key, value)

"""Hierarchical, multi-source settings management

This module provides a framework for implementing a system where
information items can be read from and written to any number of sources.
These sources are ordered to implement a simple query precedence rule.
An example of such a system is the layered Git config setup, with
system, global, local and other scopes.

The framework is built on three main classes:

- :class:`Setting`: an individual information item
- :class:`Source`: base class for a settings provider
- :class:`Settings`: the top-level API for a multi-source settings manager


Basic usage
-----------

To establish a settings manager instance one needs to create an instance of
:class:`Settings` and supply it with any instances of sources that the manager
should consider. Importantly, the order in which the sources are declared also
represents the precedence rule for reporting. Items from sources declared first
take precedence over sources declared later.

>>> from datasalad.settings import Settings, Environment, Defaults
>>> defaults = Defaults()
>>> settings = Settings(
...     {
...         'env': Environment(var_prefix='myapp_'),
...         # any number of additional sources could be here
...         'defaults': defaults,
...     }
... )

It often makes sense to use a dedicated instance of :class:`Defaults` (a
variant of :class:`InMemory`) as a base source. It can be populated on import
to collect all default settings of an application, and simplifies
implementations, because all possible settings are known to this instance.

>>> defaults['myconf'] = Setting('default-value')
>>> settings['myconf'].value
'default-value'

It is also possible to equip a setting with a callable that performs
type-coercion or validation:

>>> defaults['myapp_conf'] = Setting('5', coercer=int)
>>> settings['myapp_conf'].value
5

This coercer is inherited, if not overwritten, even when the value
with the highest precedence is retrieved from a different source,
which does not provide a coercer itself.

>>> # set value for `myapp_conf` in the `env` source
>>> settings.sources['env']['myapp_conf'] = Setting('123')
>>> settings['myapp_conf'].value
123


Advanced usage
--------------

The usage patterns already shown above are often all that is needed.
However, the framework is more flexible and allows for implementing
more flexible solutions.

Setting keys need not be of type ``str``, but can be any hashable type,
and need not necessarily be homogeneous across (or even within) individual
sources, as long as their are hashable

>>> defaults[(0, 1, 2)] = Settings(object)

There is support for multiple values registered under a single key, even within
a single source. The standard accessor methods (:meth:`__getitem__`, and
:meth:`~Settings.get`), however, always return a single item only. In case of
multiple available values, they return an item that is the composition of item
properties with the highest precedence. In contrast, the
:meth:`~Settings.getall`) method return all items across all sources as
a ``tuple``.

The :class:`Settings` class does not support setting values. Instead, the
desired source has to be selected explicitly via the :meth:`~Settings.sources`
method (as shown in the example above). This allows for individual sources to
offer an API and behavior that is optimally tuned for a particular source type,
rather than be constrained by a common denominator across all possible source
types. Sources are registered and selected via a unique, use case specific
identifier. This should make clear what kind of source is being written to in
application code.

It is also possible to use this framework with custom :class:`Setting`
subclasses, possibly adding properties or additional methods. The
:class:`Settings` class variable :attr:`~Settings.item_type` can take
a type that is used for returning default values.


Implement custom sources
------------------------

Custom sources can be implemented by subclassing
:class:`~datasalad.settings.Source`, and implementing methods for its
``dict``-like interface. Different (abstract) base classes are provided for
common use cases.

- :class:`~datasalad.settings.Source`
- :class:`~datasalad.settings.WritableSource`
- :class:`~datasalad.settings.WritableMultivalueSource`
- :class:`~datasalad.settings.CachingSource`

:class:`~datasalad.settings.Source` is the most basic class, suitable
for any read-only source. It requires implementing the following
private methods (see the class documentation for details):

- :meth:`~datasalad.settings.Source._reinit`
- :meth:`~datasalad.settings.Source._load`
- :meth:`~datasalad.settings.Source._get_item`
- :meth:`~datasalad.settings.Source._get_keys`

:class:`~datasalad.settings.WritableSource` extends the interface
with methods for modification of a writable source, and requires
the additional implementation of:

- :meth:`~datasalad.settings.Source._set_item`
- :meth:`~datasalad.settings.Source._del_item`

The property :meth:`~datasalad.settings.WritableSource.is_writable` returns
``True`` by default. It can be reimplemented to report a particular source
instance as read-only, even if it is theoretically writable, for example due to
insufficient permissions.

:class:`~datasalad.settings.CachingSource` is a writable source implementation
with an in-memory cache. It only requires implementing
:meth:`~datasalad.settings.Source._load` when set items shall not be written to
the underlying source, but are only cached in memory. Otherwise, all standard
getters and setters need to be wrapped accordingly.

Lastly, :class:`~datasalad.settings.InMemory` is a readily usable,
"source-less" items source, which is also the basis for
:class:`~datasalad.settings.Defaults`.


Notes on type-coercion and validation
-------------------------------------

Type-coercion and validation is solely done on access of a
:class:`~datasalad.settings.setting.Setting` instance's
:attr:`~datasalad.settings.setting.Setting.value` property.  There is no
on-load validation to reject invalid configuration immediately. This approach
is taken to avoid spending time on items that might never actually get
accessed.

There is also no generic on-write validation. This has to be done for each
source implementation separately and explicitly. There is no assumption of
homogeneity regarding what type and values are acceptable across sources.


API reference
-------------

.. currentmodule:: datasalad.settings
.. autosummary::
   :toctree: generated

   Settings
   Setting
   Source
   WritableSource
   WritableMultivalueSource
   CachingSource
   Environment
   InMemory
   Defaults
   UnsetValue
"""

from __future__ import annotations

from .defaults import Defaults
from .env import Environment
from .setting import (
    Setting,
    UnsetValue,
)
from .settings import Settings
from .source import (
    CachingSource,
    InMemory,
    Source,
    WritableMultivalueSource,
    WritableSource,
)

__all__ = [
    'CachingSource',
    'Defaults',
    'Environment',
    'InMemory',
    'Setting',
    'Settings',
    'Source',
    'WritableSource',
    'WritableMultivalueSource',
    'UnsetValue',
]

The `datasalad` documentation
=============================

``datasalad`` is a pure-Python library with a collection of utilities for
working with data in the vicinity of Git and git-annex.  While this is a
foundational library from and for the `DataLad project
<https://datalad.org>`__, its implementations are standalone, and are meant to
be equally well usable outside the DataLad system.

A focus of this library is efficient communication with subprocesses, such as
Git or git-annex commands, which read and produce data in some format. The
library provides utilities to integrate such subprocess in Python algorithms,
for example, to iteratively amend information in JSON-lines formatted data
streams that are retrieved in arbitrary chunks over a network connection.

Here is a simple demo how an iterable with inputs can be fed to the ``cat``
shell command, while reading its output back as a Python iterable.


.. code-block:: python

    >>> with iter_subproc(
    ...     ['cat'],
    ...     inputs=[b'one', b'two', b'three'],
    ... ) as proc:
    ...     for chunk in proc:
    ...         print(chunk)
    b'one'
    b'two'
    b'three'


Package overview
----------------

Also see the :ref:`modindex`.

.. currentmodule:: datasalad
.. autosummary::
   :toctree: generated

   runners
   iterable_subprocess
   itertools


Why ``datasalad``?
------------------

This is a base library for DataLad, hence the name ``Data-sa-Lad``.  The ``sa``
might stand for "support assemblage", or "smart assets".  More importantly, the
library is a mixture of more-or-less standalone utilties that "make up the
salad".

After ~10 years of developing DataLad, these utilities have been factored out
of the codebase to form a clearer, faster, better documented, and more
accessible set of building blocks for the next decade.


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

The `datasalad` documentation
=============================

This is a pure-Python library with a collection of utilities for working with
data in the vicinity of Git and git-annex.  While this is a foundational
library from and for the `DataLad project <https://datalad.org>`__, its
implementations are standalone, and are meant to be equally well usable outside
the DataLad system.

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

.. currentmodule:: datasalad
.. autosummary::
   :toctree: generated

   runners
   iterable_subprocess


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

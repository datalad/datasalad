The `datasalad` documentation
=============================

``datasalad`` is a pure-Python library with a collection of utilities for
working with data in the vicinity of Git and git-annex.  While this is a
foundational library from and for the `DataLad project
<https://datalad.org>`__, its implementations are standalone, and are meant to
be equally well usable outside the DataLad system.

A focus of this library is efficient communication with subprocesses, such as
Git or git-annex commands, which read and produce data in some format.

Here is a demo of what can be accomplished with this library. The following
code queries a remote git-annex repository via a ``git annex find`` command
running over an SSH connection in batch-mode. The output in JSON-lines format
is then itemized and decoded to native Python data types. Both inputs and
outputs are iterables with meaningful items, even though at a lower level
information is transmitted as an arbitrarily chunked byte stream.

.. code-block:: python

    >>> from more_itertools import intersperse
    >>> from pprint import pprint
    >>> from datasalad.runners import iter_subproc
    >>> from datasalad.itertools import (
    ...     itemize,
    ...     load_json,
    ... )

    >>> # a bunch of photos we are interested in
    >>> interesting = [
    ...     b'DIY/IMG_20200504_205821.jpg',
    ...     b'DIY/IMG_20200505_082136.jpg',
    ... ]

    >>> # run `git-annex find` on a remote server in a repository
    >>> # that has these photos in the worktree.
    >>> with iter_subproc(
    ...     ['ssh', 'photos@pididdy.local',
    ...      'git -C "collections" annex find --json --batch'],
    ...     # the remote process is fed the file names,
    ...     # and a newline after each one to make git-annex write
    ...     # a report in JSON-lines format
    ...     inputs=intersperse(b'\n', interesting),
    ... ) as remote_annex:
    ...     # we loop over the output of the remote process.
    ...     # this is originally a byte stream downloaded in arbitrary
    ...     # chunks, so we itemize at any newline separator.
    ...     # each item is then decoded from JSON-lines format to
    ...     # native datatype
    ...     for rec in load_json(itemize(remote_annex, sep=b'\n')):
    ...         # for this demo we just pretty-print it
    ...         pprint(rec)
    {'backend': 'SHA256E',
     'bytesize': '3357612',
     'error-messages': [],
     'file': 'DIY/IMG_20200504_205821.jpg',
     'hashdirlower': '853/12f/',
     'hashdirmixed': '65/qp/',
     'humansize': '3.36 MB',
     'key': 'SHA256E-s3357612--700a52971714c2707c2de975f6015ca14d1a4cdbbf01e43d73951c45cd58c176.jpg',
     'keyname': '700a52971714c2707c2de975f6015ca14d1a4cdbbf01e43d73951c45cd58c176.jpg',
     'mtime': 'unknown'}
    {'backend': 'SHA256E',
     'bytesize': '3284291',
     ...


Package overview
----------------

Also see the :ref:`modindex`.

.. currentmodule:: datasalad
.. autosummary::
   :toctree: generated

   gitpathspec
   iterable_subprocess
   itertools
   runners
   settings


Why ``datasalad``?
------------------

This is a base library for DataLad, hence the name ``Data-sa-Lad``.  The ``sa``
might stand for "support assemblage", or "smart assets".  More importantly, the
library is a mixture of more-or-less standalone utilities that "make up the
salad".

After ~10 years of developing DataLad, these utilities have been factored out
of the codebase to form a clearer, faster, better documented, and more
accessible set of building blocks for the next decade.


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

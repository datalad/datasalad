# DataSALad

[![GitHub release](https://img.shields.io/github/release/datalad/datasalad.svg)](https://GitHub.com/datalad/datasalad/releases/)
[![PyPI version fury.io](https://badge.fury.io/py/datasalad.svg)](https://pypi.python.org/pypi/datasalad/)
[![Build status](https://ci.appveyor.com/api/projects/status/wtksrottgt82h2ra/branch/main?svg=true)](https://ci.appveyor.com/project/mih/datasalad/branch/main)
[![codecov](https://codecov.io/gh/datalad/datasalad/branch/main/graph/badge.svg?token=VSO592NATM)](https://codecov.io/gh/datalad/datasalad)
[![Documentation Status](https://readthedocs.org/projects/datasalad/badge/?version=latest)](https://datasalad.readthedocs.io/latest/?badge=latest)
[![Maintainability](https://api.codeclimate.com/v1/badges/5195c4a515351e791b6b/maintainability)](https://codeclimate.com/github/datalad/datasalad/maintainability)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

This is a pure-Python library with a collection of utilities for working with
data in the vicinity of Git and git-annex.  While this is a foundational
library from and for the [DataLad project](https://datalad.org), its
implementations are standalone, and are meant to be equally well usable outside
the DataLad system.

A focus of this library is efficient communication with subprocesses, such as
Git or git-annex commands, which read and produce data in some format.

Here is a demo of what can be accomplished with this library. The following
code queries a remote git-annex repository via a `git annex find` command
running over an SSH connection in batch-mode. The output in JSON-lines format
is then itemized and decoded to native Python data types. Both inputs and
outputs are iterables with meaningful items, even though at a lower level
information is transmitted as an arbitrarily chunked byte stream.

```py
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
...     # native datatypes
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
```

## Developing with datasalad

API stability is important, just as adequate semantic versioning, and informative
changelogs.

### Public vs internal API

Anything that can be imported directly from any of the sub-packages in
`datasalad` is considered to be part of the public API. Changes to this API
determine the versioning, and development is done with the aim to keep this API
as stable as possible. This includes signatures and return value behavior.

As an example: `from datasalad.runners import iter_git_subproc` imports a
part of the public API, but `from datasalad.runners.git import
iter_git_subproc` does not.

### Use of the internal API

Developers can obviously use parts of the non-public API. However, this should
only be done with the understanding that these components may change from one
release to another, with no guarantee of transition periods, deprecation
warnings, etc.

Developers are advised to never reuse any components with names starting with
`_` (underscore). Their use should be limited to their individual subpackage.

## Contributing

Contributions to this library are welcome! Please see the [contributing
guidelines](https://github.com/datalad/datasalad/blob/main/CONTRIBUTING.md) for
details on scope and style of potential contributions.

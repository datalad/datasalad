# DataSALad

[![GitHub release](https://img.shields.io/github/release/datalad/datasalad.svg)](https://GitHub.com/datalad/datasalad/releases/)
[![PyPI version fury.io](https://badge.fury.io/py/datasalad.svg)](https://pypi.python.org/pypi/datasalad/)
[![Build status](https://ci.appveyor.com/api/projects/status/wtksrottgt82h2ra/branch/main?svg=true)](https://ci.appveyor.com/project/mih/datasalad/branch/main)
[![codecov](https://codecov.io/gh/datalad/datasalad/branch/main/graph/badge.svg?token=VSO592NATM)](https://codecov.io/gh/datalad/datasalad)
[![Documentation Status](https://readthedocs.org/projects/datasalad/badge/?version=latest)](https://datasalad.readthedocs.io/latest/?badge=latest)

This is a pure-Python library with a collection of utilities for working with
data in the vicinity of Git and git-annex.  While this is a foundational
library from and for the [DataLad project](https://datalad.org), its
implementations are standalone, and are meant to be equally well usable outside
the DataLad system.

A focus of this library is efficient communication with subprocesses, such as
Git or git-annex commands, which read and produce data in some format. The
library provides utilities to integrate such subprocess in Python algorithms,
for example, to iteratively amend information in JSON-lines formatted data
streams that are retrieved in arbitrary chunks over a network connection.

Here is a simple demo how an iterable with inputs can be fed to the ``cat``
shell command, while reading its output back as a Python iterable.

```py
>>> with iter_subproc(['cat'], inputs=[b'one', b'two', b'three']) as proc:
...     for chunk in proc:
...         print(chunk)
b'one'
b'two'
b'three'
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
guidelines](CONTRIBUTING.md) for details on scope on styles of potential
contributions.

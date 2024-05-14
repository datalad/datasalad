# DataSALad

[![GitHub release](https://img.shields.io/github/release/datalad/datasalad.svg)](https://GitHub.com/datalad/datasalad/releases/)
[![PyPI version fury.io](https://badge.fury.io/py/datasalad.svg)](https://pypi.python.org/pypi/datasalad/)
[![Build status](https://ci.appveyor.com/api/projects/status/wtksrottgt82h2ra/branch/main?svg=true)](https://ci.appveyor.com/project/mih/datasalad/branch/main)


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

## Acknowledgements

This DataLad extension was developed with funding from the Deutsche
Forschungsgemeinschaft (DFG, German Research Foundation) under grant SFB 1451
([431549029](https://gepris.dfg.de/gepris/projekt/431549029), INF project).

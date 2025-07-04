# Contributing to `datasalad`

- [Developer cheat sheet](#developer-cheat-sheet)
- [What contributions are most suitable for `datasalad`](#when-should-i-consider-a-contribution-to-datasalad)
- [Code organization](#code-organization)
- [Style guide](#contribution-style-guide)


## Developer cheat sheet

[Hatch](https://hatch.pypa.io) is used as a convenience solution for packaging and development tasks.
Hatch takes care of managing dependencies and environments, including the Python interpreter itself.
If not installed yet, installing via [uv](https://docs.astral.sh/uv) is recommended (`uv tool install hatch`).

Below is a list of some provided convenience commands.
An accurate overview of provided convenience scripts can be obtained by running: `hatch env show`.
All command setup can be found in `pyproject.toml`, and given alternatively managed dependencies, all commands can also be used without `hatch`.

### Run the tests (with coverage reporting)

```
hatch test [--cover] [--all]
```

This can also be used to run tests for a specific Python version only:

```
hatch test -i py=3.10 [<select tests>]
```

### Build the HTML documentation (under `docs/_build/html`)

```
hatch run docs:build
# clean with
hatch run docs:clean
```

### Check type annotations

```
hatch run types:check
```

### Check commit messages for compliance with [Conventional Commits](https://www.conventionalcommits.org)

```
hatch run cz:check-commits
```

### Show would-be auto-generated changelog for the next release

```
hatch run cz:show-changelog
```

### Create a new release

```
hatch run cz:bump-version
```

The new version is determined automatically from the nature of the (conventional) commits made since the last release.
A changelog is generated and committed.

In cases where the generated changelog needs to be edited afterwards (typos, unnecessary complexity, etc.), the created version tag needs to be advanced.


### Build a new source package and wheel

```
hatch build
```

### Publish a new release to PyPi

```
hatch publish
```


## When should I consider a contribution to `datasalad`?

This project's main purpose is to be a core library for DataLad.
But it is just a library, not a component in the DataLad system.
This means that library components cannot rely on a particular "DataLad setup".
Neither the presence of DataLad datasets (rather than any Git/git-annex repository), nor a particular DataLad-enforced configuration, or dependencies, or runtime behavior can be assumed.
If such assumptions are made, the respective code is likely not a suitable contribution.

It is a supported scenario to use this library outside the context of a DataLad package, and contributions must be evaluated with respect to implied addition of further software dependencies.
Code that implements support for a particular (web)service and/or relies on a special-purpose support package is likely better contributed elsewhere (see below).

Code "for working with data" that has wide applicability, some previous real-world exposure, good tests and a light dependency footprint is a candidate for inclusion into the library.

### What contributions should be directed elsewhere?

Special interest, highly domain-specific functionality is likely better suited for a topical library of DataLad extension package.
Generic functionality for the DataLad system is best directed to the `datalad` core package.
If in doubt, it is advisable to file an issue and ask for feedback before preparing a contribution.

## Code organization

In `datasalad`, all code is organized in shallow sub-packages. Each sub-package is located in a directory within the `datasalad` package.

Consequently, there are no top-level source files other than a few exceptions for technical reasons (`__init__.py`, `conftest.py`).

A sub-package contains any number of code files, and a `tests` directory with all test implementations for that particular sub-package, and only for that sub-package. Other, deeper directory hierarchies are not to be expected.

There is no limit to the number of files. Contributors should strive for files with less than 500 lines of code.

Within a sub-package, code should generally use relative imports. The corresponding tests should also import the tested code via relative imports.

Code users should be able to import the most relevant functionality from the sub-package's `__init__.py`. Only items importable from the sub-package's top-level are considered to be part of its "public" API. If a sub-module is imported in the sub-package's `__init__.py`, consider adding `__all__` to the sub-module to restrict wildcard imports from the sub-module, and to document what is considered to be part of the "public" API.

Sub-packages should be as self-contained as possible. This means that any organization principles like *all-exceptions-go-into-a-single-location-in-datasalad* do not immediately/necessarily apply. For example, each sub-package should define its special-purpose exceptions separately from others. When functionality is shared between sub-packages, absolute imports should be made.

## Contribution style guide

A contribution must be complete with code, tests, and documentation.

`datasalad` is a core library for a software ecosystem. Therefore, tests are essential. A high test-coverage is desirable. Contributors should aim for near-complete coverage (or better). Tests must be dedicated for the code of a particular contribution. It is not sufficient, if other code happens to also exercise a new feature.

### Documentation

Docstrings should be complete with information on parameters, return values, and exception behavior. Documentation should be added to and rendered with the sphinx-based documentation.

### Commits

Commits and commit messages must be [Conventional Commits](https://www.conventionalcommits.org). Their compliance is checked for each pull request. The following commit types are recognized:

- `feat`: introduces a new feature
- `fix`: address a problem, fix a bug
- `doc`: update the documentation
- `rf`: refactor code with no change of functionality
- `perf`: enhance performance of existing functionality
- `test`: add/update/modify test implementations
- `ci`: change CI setup
- `style`: beautification
- `chore`: results of routine tasks, such as changelog updates
- `revert`: revert a previous change
- `bump`: version update

Any breaking change must have at least one line of the format

    BREAKING CHANGE: <summary of the breakage>

in the body of the commit message that introduces the breakage. Breaking changes can be introduced in any type of commit. Any number of breaking changes can be described in a commit message (one per line). Breaking changes trigger a major version update, and form a dedicated section in the changelog.

### Pull requests

Contributions submitted via a pull-request (PR), are expected to be a clear, self-describing series of commits. The PR description is largely irrelevant, and could be used for a TODO list, or conversational content. All essential information concerning the code and changes **must** be contained in the commit messages.

Commit series should be "linear", with individual commits being self-contained, well-described changes.

If possible, only loosely related changes should be submitted in separate PRs to simplify reviewing and shorten time-to-merge.

Long-standing, inactive PRs (draft mode or not) are frowned upon, as they drain attention. It is often better to close a PR and open a new one, once work resumes. Maintainers may close inactive PRs for this reason at any time.

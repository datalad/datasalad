from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING

from datasalad.gitpathspec.pathspec import GitPathSpec

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import (
        PurePosixPath,
    )


class GitPathSpecs:
    """Convenience container for any number of pathspecs (or none)

    This class can facilitate implementing support for pathspec-constraints,
    including scenarios involving submodule recursion.

    >>> from pathlib import PurePosixPath
    >>> # can accept a "default" argument for no pathspecs
    >>> ps = GitPathSpecs(None)
    >>> not ps
    True
    >>> ps.arglist()
    []
    >>> # deal with any number of pathspecs
    >>> ps = GitPathSpecs(['*.jpg', 'dir/*.png'])
    >>> ps.any_match_subdir(PurePosixPath('dummy'))
    True
    >>> ps.for_subdir(PurePosixPath('dir'))
    GitPathSpecs(['*.jpg', '*.png'])
    """

    def __init__(
        self,
        pathspecs: Iterable[str | GitPathSpec] | GitPathSpecs | None,
    ):
        """Pathspecs can be given as an iterable (string-form and/or
        ``GitPathSpec``), another ``GitPathSpecs`` instance, or ``None``.
        ``None``, or empty iterable indicate a 'no constraint' scenario,
        equivalent to a single ``':'`` pathspec.
        """
        self._pathspecs: tuple[GitPathSpec, ...] | None = None

        if pathspecs is None:
            self._pathspecs = None
            return

        if isinstance(pathspecs, GitPathSpecs):
            self._pathspecs = pathspecs.pathspecs or None
            return

        # we got something that needs converting
        self._pathspecs = tuple(
            ps if isinstance(ps, GitPathSpec) else GitPathSpec.from_pathspec_str(ps)
            for ps in pathspecs
        )
        if not self._pathspecs:
            msg = (
                f'{pathspecs!r} did not contain any pathspecs. '
                'To indicate "no pathspec constraints" use the '
                '":" pathspec or `None`.'
            )
            raise ValueError(msg)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}([{', '.join(repr(p) for p in self.arglist())}])"
        )

    def __len__(self) -> int:
        return len(self._pathspecs) if self._pathspecs is not None else 0

    def __eq__(self, obj):
        return self.pathspecs == obj.pathspecs

    # TODO: lru_cache decorator?
    # this would prevent repeated conversion cost for the usage pattern of
    # - test if we would have a match for a subdir
    # - run code with the matching pathspecs
    # without having to implement caching logic in client code
    def for_subdir(
        self,
        path: PurePosixPath,
    ) -> GitPathSpecs:
        """Translate pathspecs into the scope of a subdirectory

        Raises
        ------
        ValueError
          Whenever no pathspec can be translated into the scope of the target
          directory.
        """
        if not self._pathspecs:
            return GitPathSpecs(None)
        translated = list(
            chain.from_iterable(ps.for_subdir(str(path)) for ps in self._pathspecs)
        )
        if not translated:
            # not a single pathspec could be translated into the subdirectory
            # scope. This means none was applicable, and not that the whole
            # subdirectory is matched. We raise in order to allow client code
            # to distinguish a no-match from an all-match scenario. Returning
            # the equivalent of an empty list would code "no constraint",
            # rather than "no match"
            msg = f'No pathspecs translate to {path=}'
            raise ValueError(msg)
        return GitPathSpecs(translated)

    def any_match_subdir(
        self,
        path: PurePosixPath,
    ) -> bool:
        """Returns whether any pathspec could match subdirectory content

        In other words, ``False`` is returned whenever ``.for_subdir()``
        would raise ``ValueError``.

        Parameters
        ----------
        path: PurePosixPath
          Relative path of the subdirectory to run the test for.
        """
        if self._pathspecs is None:
            return True
        path_s = str(path)
        return any(ps.for_subdir(path_s) for ps in self._pathspecs)

    def arglist(self) -> list[str]:
        """Convert pathspecs to a CLI argument list

        This list is suitable for use with any Git command that supports
        pathspecs, after a ``--`` (that disables the interpretation of further
        arguments as options).

        When no pathspecs are present an empty list is returned.
        """
        if self._pathspecs is None:
            return []
        return [str(ps) for ps in self._pathspecs]

    @property
    def pathspecs(self) -> tuple[GitPathSpec, ...] | None:
        return self._pathspecs

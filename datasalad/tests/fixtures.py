"""Collection of fixtures for facilitation test implementations"""

from __future__ import annotations

from shutil import which

import pytest


def _which_cmd(cmd: str) -> str:
    binary = which(cmd)
    if not binary:
        pytest.skip(f'`{cmd}` is not available.')
        # we cannot get here, but return a str to satisfy
        # the type-checker
        return ''
    return binary


# function-scope to be able to skip each "calling" test
@pytest.fixture(autouse=False, scope='function')  # noqa: PT003
def cat_util() -> list[str]:
    """Returns command(args) list of a `cat` utility

    Skips the underlying test if no `cat` is available.

    In the future, this fixture may provide a Python-based
    `cat` replacement for testing purposed.
    """
    return [_which_cmd('cat')]


# function-scope to be able to skip each "calling" test
@pytest.fixture(autouse=False, scope='function')  # noqa: PT003
def ls_util() -> list[str]:
    """Returns command(args) list of a `ls` utility

    Skips the underlying test if no `ls` is available.
    """
    return [_which_cmd('ls')]


# function-scope to be able to skip each "calling" test
@pytest.fixture(autouse=False, scope='function')  # noqa: PT003
def funzip_util() -> list[str]:
    """Returns command(args) list of a `funzip` utility

    Skips the underlying test if no `funzip` is available.
    """
    return [_which_cmd('funzip')]

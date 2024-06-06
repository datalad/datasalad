from __future__ import annotations

import pytest

from ..exception import CommandError


def test_CommandError_minial():
    with pytest.raises(TypeError):
        # we need a command
        CommandError()
    # this is the CommandError instance with the least information:
    # the failed command
    ce = CommandError('mycmd')
    assert str(ce) == "CommandError: 'mycmd'"
    ce = CommandError(['mycmd', 'arg0'])
    assert str(ce) == "CommandError: ['mycmd', 'arg0']"


def test_command_error_rendering() -> None:
    command_error = CommandError(
        cmd="<cmd>",
        msg="<msg>",
        returncode=1,
        stdout="<stdout>",
        stderr="<stderr>",
        cwd="<cwd>",
    )

    assert command_error.to_str() == str(command_error) == \
        "CommandError: '<cmd>' failed with exitcode 1 at CWD <cwd> [<msg>]"

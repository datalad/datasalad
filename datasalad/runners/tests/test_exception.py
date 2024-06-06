from __future__ import annotations

from ..exception import CommandError


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

from __future__ import annotations

from ..exception import CommandError


def test_command_error_rendering() -> None:
    command_error = CommandError(
        cmd="<cmd>",
        msg="<msg>",
        code=1,
        stdout="<stdout>",
        stderr="<stderr>",
        cwd="<cwd>",
        kwarg1="<kwarg1>",
        kwarg2="<kwarg2>")

    result = command_error.to_str()
    assert result == \
        "CommandError: '<cmd>' failed with exitcode 1 under <cwd> [<msg>] " \
        "[info keys: kwarg1, kwarg2]"

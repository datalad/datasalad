"""Exception raised on a failed command execution
"""
from __future__ import annotations

import os
import signal


class CommandError(RuntimeError):
    """Raised when a subprocess execution fails (non-zero exit)

    Key class attributes are aligned with the ``CalledProcessError`` exception
    of the ``subprocess`` module of the Python standard library. However,
    this class is not a subclass of ``CalledProcessError``, but a subclass
    of ``RuntimeError``.

    At minimum, the command with the failed execution must be provided
    as an argument. A number of additional information items can be provided
    in addition to enable more comprehensive reporting on execution failures.

    As an addition to the ``CalledProcessError`` arguments, a ``msg`` parameter
    is supported which can be used to include contextual information on the
    command execution, for example why a command execution was attempted, or
    under which particular circumstances.
    """

    def __init__(
        self,
        cmd: str | list[str],
        msg: str = "",
        returncode: int | None = None,
        stdout: str | bytes = "",
        stderr: str | bytes = "",
        cwd: str | os.PathLike | None = None,
    ) -> None:
        RuntimeError.__init__(self, msg)
        self.cmd = cmd
        self.msg = msg
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.cwd = cwd

    def to_str(self) -> str:
        # we report the command verbatim, in exactly the form that it has
        # been given to the exception. Previously implementation have
        # beautified output by joining list-format commands with shell
        # quoting. However that implementation assumed that the command
        # actually run locally. In practice, CommandError is also used
        # to report on remote command execution failure. Reimagining
        # quoting and shell conventions based on assumptions is confusing.
        to_str = f"Command {self.cmd!r}"
        if self.returncode and self.returncode < 0:
            try:
                to_str += f" died with {signal.Signals(-self.returncode).name}"
            except ValueError:
                to_str += f" died with unknown signal {-self.returncode}"
        elif self.returncode:
            to_str += f" returned non-zero exit status {self.returncode}"
        else:
            to_str += " errored with unknown exit status"
        if self.cwd:
            # only if not under standard PWD
            to_str += f" at CWD {self.cwd}"
        if self.msg:
            # typically a command error has no specific idea
            # but we support it, because CommandError derives
            # from RuntimeError which has this feature.
            to_str += f" [{self.msg}]"

        return to_str

    def __str__(self) -> str:
        return self.to_str()

    def __repr__(self) -> str:
        descr = f"{self.__class__.__name__}({self.cmd!r}"
        for kwarg, (val, default) in dict(
            msg=(self.msg, ''),
            returncode=(self.returncode, None),
            stdout=(self.stdout, ''),
            stderr=(self.stderr, ''),
            cwd=(self.cwd, None),
        ).items():
            if val == default:
                continue
            if kwarg in ('stdout', 'stderr'):
                assert isinstance(val, (str, bytes))
                if isinstance(val, bytes):
                    descr += f", {kwarg}=b{truncate_bytes(val)!r}"
                else:
                    descr += f", {kwarg}={truncate_str(val)!r}"
            else:
                descr += f", {kwarg}={val!r}"
        descr += ')'
        return descr


def truncate_bytes(data: bytes) -> str:
    return f'<{len(data)} bytes>'


def truncate_str(text: str) -> str:
    # truncation like done below only actually shortens beyond
    # 60 chars input length
    front = 20
    back = 20
    if len(text) < (front + back + 14):
        # stringify only
        return f"{text}"
    else:
        return f"{text[:front]}<... +{len(text) - front - back} chars>" \
               f"{text[-back:]}"

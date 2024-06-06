# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Exception raise on a failed runner command execution
"""
from __future__ import annotations

import logging
import os
from collections import Counter
from typing import (
    Any,
    Optional,
)

lgr = logging.getLogger('datalad.runner.exception')


class CommandError(RuntimeError):
    """Thrown if a command call fails.

    Note: Subclasses should override `to_str` rather than `__str__` because
    `to_str` is called directly in datalad.cli.main.
    """

    def __init__(
        self,
        cmd: str | list[str] = "",
        msg: str = "",
        code: Optional[int] = None,
        stdout: str | bytes = "",
        stderr: str | bytes = "",
        cwd: str | os.PathLike | None = None,
        **kwargs: Any,
    ) -> None:
        RuntimeError.__init__(self, msg)
        self.cmd = cmd
        self.msg = msg
        self.code = code
        self.stdout = stdout
        self.stderr = stderr
        self.cwd = cwd
        self.kwargs = kwargs

    def to_str(self) -> str:
        to_str = "{}: ".format(self.__class__.__name__)
        cmd = self.cmd
        if cmd:
            # we report the command verbatim, in exactly the form that it has
            # been given to the exception. Previously implementation have
            # beautified output by joining list-format commands with shell
            # quoting. However that implementation assumed that the command
            # actually run locally. In practice, CommandError is also used
            # to report on remote command execution failure. Reimagining
            # quoting and shell conventions based on assumptions is confusing.
            to_str += f"'{cmd}'"
        if self.code:
            to_str += " failed with exitcode {}".format(self.code)
        if self.cwd:
            # only if not under standard PWD
            to_str += " under {}".format(self.cwd)
        if self.msg:
            # typically a command error has no specific idea
            to_str += " [{}]".format(self.msg)

        if self.kwargs:
            to_str += " [info keys: {}]".format(
                ', '.join(self.kwargs.keys()))

            if 'stdout_json' in self.kwargs:
                to_str += _format_json_error_messages(
                    self.kwargs['stdout_json'])

        return to_str

    def __str__(self) -> str:
        return self.to_str()


def _format_json_error_messages(recs: list[dict]) -> str:
    # there could be many, condense
    msgs: Counter[str] = Counter()
    for r in recs:
        if r.get('success'):
            continue
        msg = '{}{}'.format(
            ' {}\n'.format(r['note']) if r.get('note') else '',
            '\n'.join(r.get('error-messages', [])),
        )
        if 'file' in r or 'key' in r:
            msgs[msg] += 1

    if not msgs:
        return ''

    return '\n>{}'.format(
        '\n> '.join(
            '{}{}'.format(
                m,
                ' [{} times]'.format(n) if n > 1 else '',
            )
            for m, n in msgs.items()
        )
    )

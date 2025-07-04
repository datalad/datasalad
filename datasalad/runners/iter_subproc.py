from __future__ import annotations

from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

from datasalad import iterable_subprocess

try:
    # we "type-ignore" the next line, because we run mypy configured
    # to anticipate an old Python 3.8, but likely run on a newer one
    from shutil import COPY_BUFSIZE  # type: ignore
except ImportError:  # pragma: no cover
    import sys

    # too old
    # backported windows default from from Python 3.10.
    COPY_BUFSIZE = 1024 * 1024 if sys.platform.startswith('win') else 64 * 1024

__all__ = ['iter_subproc']


def iter_subproc(
    args: list[str],
    *,
    inputs: Iterable[bytes] | None = None,
    chunk_size: int = COPY_BUFSIZE,
    cwd: Path | None = None,
    bufsize: int = -1,
):
    """Context manager to communicate with a subprocess using iterables

    This offers a higher level interface to subprocesses than Python's
    built-in ``subprocess`` module. It allows a subprocess to be naturally
    placed in a chain of iterables as part of a data processing pipeline.
    It is also helpful when data won't fit in memory and has to be streamed.

    This is a convenience wrapper around ``datasalad.iterable_subprocess``,
    which itself is a slightly modified (for use on Windows) fork of
    https://github.com/uktrade/iterable-subprocess, written by
    Michal Charemza.

    This function provides a context manager.
    On entering the context, the subprocess is started, the thread to read
    from standard error is started, the thread to populate subprocess
    input is started.
    When running, the standard input thread iterates over the input,
    passing chunks to the process, while the standard error thread
    fetches the error output, and while the main thread iterates over
    the process's output from client code in the context.

    On context exit, the main thread closes the process's standard output,
    waits for the standard input thread to exit, waits for the standard error
    thread to exit, and wait for the process to exit. If the process exited
    with a non-zero return code, a ``CommandError`` is raised,
    containing the process's return code.

    If the context is exited due to an exception that was raised in the
    context, the main thread terminates the process via ``Popen.terminate()``,
    closes the process's standard output, waits for the standard input
    thread to exit, waits for the standard error thread to exit, waits
    for the process to exit, and re-raises the exception.

    >>> # regular execution, no input iterable
    >>> with iter_subproc(['printf', 'test']) as proc:
    ...     for chunk in proc:
    ...         print(chunk)
    b'test'
    >>> # feed subprocess stdin from an iterable
    >>> with iter_subproc(['cat'], inputs=[b'one', b'two', b'three']) as proc:
    ...     for chunk in proc:
    ...         print(chunk)
    b'onetwothree'

    Note, if an exception is raised in the context, this exception will bubble
    up to the main thread. That means no ``CommandError`` will
    be raised if the subprocess exited with a non-zero return code.
    To access the return code in case of an exception inside the context,
    use the ``returncode``-attribute of the ``as``-variable.
    This object will always contain the return code of the subprocess.
    For example, the following code will raise a ``StopIteration``-exception
    in the context (by repeatedly using :func:`next`). The subprocess
    will exit with ``2`` due to the illegal option ``-@``, and no
    ``CommandError`` is raised. The return code is read from
    the variable ``ls_stdout``

    .. code-block:: python

     >> try:
     ..     with iter_subproc(['ls', '-@']) as ls_stdout:
     ..         while True:
     ..             next(ls_stdout)
     .. except Exception as e:
     ..     print(repr(e), ls_stdout.returncode)
     StopIteration() 2


    Parameters
    ----------
    args: list
      Sequence of program arguments to be passed to ``subprocess.Popen``.
    inputs: iterable, optional
      If given, chunks of ``bytes`` to be written, iteratively, to the
      subprocess's ``stdin``.
    chunk_size: int, optional
      Size of chunks to read from the subprocess's stdout/stderr in bytes.
    cwd: Path
      Working directory for the subprocess, passed to ``subprocess.Popen``.
    bufsize: int, optional
      Buffer size to use for the subprocess's ``stdin``, ``stdout``, and
      ``stderr``. See ``subprocess.Popen`` for details.

    Returns
    -------
    contextmanager
    """
    return iterable_subprocess.iterable_subprocess(
        args,
        () if inputs is None else inputs,
        chunk_size=chunk_size,
        cwd=cwd,
        bufsize=bufsize,
    )

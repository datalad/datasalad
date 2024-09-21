"""High-level utilities for execution of subprocesses

This module provides relevant components for subprocess execution.
Execution errors are communicated with the
:class:`~datasalad.runners.CommandError` exception.

.. currentmodule:: datasalad.runners
.. autosummary::
   :toctree: generated

   CommandError
   iter_subproc
"""

__all__ = ['CommandError', 'iter_subproc']

from .exception import CommandError
from .iter_subproc import iter_subproc

"""High-level utilties for execution of subprocesses

This module provides relevant components for subprocess execution.
Execution errors are communicated with the
:class:`~datasalad.runners.CommandError` exception.

.. currentmodule:: datasalad.runners
.. autosummary::
   :toctree: generated

   CommandError
"""

__all__ = ['CommandError']

from .exception import CommandError

"""Various iterators, e.g., for subprocess pipelining and output processing

.. currentmodule:: datasalad.itertools
.. autosummary::
   :toctree: generated

    align_pattern
    decode_bytes
    itemize
    load_json
    load_json_with_flag
    route_out
    route_in
"""

__all__ = [
    'align_pattern',
    'decode_bytes',
    'itemize',
    'load_json',
    'load_json_with_flag',
    'StoreOnly',
    'route_in',
    'route_out',
]

from .align_pattern import align_pattern
from .decode_bytes import decode_bytes
from .itemize import itemize
from .load_json import (
    load_json,
    load_json_with_flag,
)
from .reroute import (
    StoreOnly,
    route_in,
    route_out,
)

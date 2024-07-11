"""Get strings decoded from chunks of bytes"""

from __future__ import annotations

from typing import (
    Generator,
    Iterable,
)

__all__ = ['decode_bytes']


def decode_bytes(
    iterable: Iterable[bytes],
    *,
    encoding: str = 'utf-8',
    backslash_replace: bool = True,
) -> Generator[str, None, None]:
    """Decode bytes in an ``iterable`` into strings

    This function decodes ``bytes`` or ``bytearray`` into ``str`` objects,
    using the specified encoding. Importantly, the decoding input can
    be spread across multiple chunks of heterogeneous sizes, for example
    output read from a process or pieces of a download.

    There is no guarantee that exactly one output chunk will be yielded for
    every input chunk. Input byte strings might be split at error-locations, or
    might be joined if a multi-byte encoding is spread over multiple chunks. If
    ``decode_bytes()`` is used together with ``itemize()``, it is advisable to
    wrap ``itemize()`` around ``decode_bytes()`` to avoid an impact on the
    number and nature of yielded items with respect to the desired itemization
    pattern.

    Multi-byte encodings that are spread over multiple byte chunks are
    supported, and chunks are joined as necessary. For example, the utf-8
    encoding for ö is ``b'\\xc3\\xb6'``.  If the encoding is split in the
    middle because a chunk ends with ``b'\\xc3'`` and the next chunk starts
    with ``b'\\xb6'``, a naive decoding approach like the following would fail:

    .. code-block:: python

       >>> [chunk.decode() for chunk in [b'\\xc3', b'\\xb6']]     # doctest: +SKIP
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "<stdin>", line 1, in <listcomp>
        UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc3 in position 0: unexpected end of data

    Compared to:

    .. code-block:: python

        >>> from datasalad.itertools import decode_bytes
        >>> tuple(decode_bytes([b'\\xc3', b'\\xb6']))
        ('ö',)

    Input chunks are only joined, if it is necessary to properly decode bytes:

    .. code-block:: python

        >>> from datasalad.itertools import decode_bytes
        >>> tuple(decode_bytes([b'\\xc3', b'\\xb6', b'a']))
        ('ö', 'a')

    If ``backslash_replace`` is ``True``, undecodable bytes will be
    replaced with a backslash-substitution. Otherwise,
    undecodable bytes will raise a ``UnicodeDecodeError``:

    .. code-block:: python

        >>> tuple(decode_bytes([b'\\xc3']))
        ('\\\\xc3',)
        >>> tuple(decode_bytes([b'\\xc3'], backslash_replace=False))    # doctest: +SKIP
        Traceback (most recent call last):
            ...
        UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc3 in position 1: invalid continuation byte

    Backslash-replacement of undecodable bytes is an ambiguous mapping,
    because, for example, ``b'\\xc3'`` can already be present in the input.

    Parameters
    ----------
    iterable: Iterable[bytes]
        Iterable that yields bytes that should be decoded
    encoding: str (default: ``'utf-8'``)
        Encoding to be used for decoding.
    backslash_replace: bool (default: ``True``)
        If ``True``, backslash-escapes are used for undecodable bytes. If
        ``False``, a ``UnicodeDecodeError`` is raised if a byte sequence cannot
        be decoded.

    Yields
    ------
    str
        Decoded strings that are generated by decoding the data yielded by
        ``iterable`` with the specified ``encoding``

    Raises
    ------
    UnicodeDecodeError
        If ``backslash_replace`` is ``False`` and the data yielded by
        ``iterable`` cannot be decoded with the specified ``encoding``
    """

    def handle_decoding_error(
        position: int, exc: UnicodeDecodeError
    ) -> tuple[int, str]:
        """Handle a UnicodeDecodeError"""
        if not backslash_replace:
            # Signal the error to the caller
            raise exc
        return (
            position + exc.end,
            joined_data[position : position + exc.start].decode(encoding)
            + joined_data[position + exc.start : position + exc.end].decode(
                encoding, errors='backslashreplace'
            ),
        )

    joined_data = b''
    pending_error = None
    position = 0
    for chunk in iterable:
        joined_data += chunk
        while position < len(joined_data):
            try:
                yield joined_data[position:].decode(encoding)
                joined_data = b''
            except UnicodeDecodeError as e:
                # If an encoding error occurs, we first check whether it was
                # in the middle of `joined_data` or whether it extends until the
                # end of `joined_data`.
                # If it occurred in the middle of
                # `joined_data`, we replace it with backslash encoding or
                # re-raise the decoding error.
                # If it occurred at the end of `joined_data`, we wait for the
                # next chunk, which might fix the problem.
                if position + e.end == len(joined_data):
                    # Wait for the next chunk, which might fix the problem
                    pending_error = e
                    break
                else:
                    pending_error = None
                    position, string = handle_decoding_error(position, e)
                    yield string

    if pending_error:
        # If the last chunk has a decoding error at the end, process it.
        position, string = handle_decoding_error(position, pending_error)
        if string:
            yield string

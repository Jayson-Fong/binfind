"""
Locate entries within a file-like object

Utilities to identify an entry within a
file-like object given an offset in a file.
"""

from typing import BinaryIO


def get_entry(
        obj: BinaryIO,
        offset: int,
        minimum_entry_size: int = 1,
        maximum_entry_size: int = 128,
        delimiter: bytes = b"\n",
) -> tuple[bytes, int, int]:
    """
    Find an entry at or after the given offset.

    The offset is ideal where the delimiter prior to the desired
    entry begins except when the offset is 0. If the program
    cannot locate the starting or ending delimiter, it will raise
    an exception. When the offset points to an entry that is not
    the beginning of the delimiter for an entry and is not 0,
    it will attempt to locate the next entry. The EOF is treated
    as if a delimiter. The minimum and maximum entry sizes are
    not strictly enforced, but instead used as heuristics.

    Args:
        obj: A file-like object opened in binary mode.
        offset: Byte offset in the file to start searching.
        minimum_entry_size: Minimum number of bytes an entry includes.
        maximum_entry_size: Maximum number of bytes an entry includes.
        delimiter: A single byte delimiter that delimits entries.

    Returns:
        tuple[bytes, int, int]: A tuple containing:
            - The extracted entry as bytes (excluding delimiters).
            - The starting byte index of the entry within the file.
            - The ending byte index of the entry within the file.

    Raises:
        RuntimeError: If the starting or ending delimiter cannot
            be found within the read limits.
    """

    # Jump to our offset
    obj.seek(offset)

    # Get our initial line
    initial_line: bytes = obj.read(maximum_entry_size + len(delimiter) * 2)
    initial_line_length: int = len(initial_line)

    # Locate our starting delimiter. However, if our offset is 0,
    # we take it that we have already passed the delimiter.
    if offset == 0:
        entry_start: int = 0
    else:
        entry_start: int = initial_line.find(delimiter)
        if entry_start == -1:
            raise RuntimeError(f"Failed to locate entry start delimiter for offset {offset!s}")

        # The content before our delimiter is not necessary, so remove it
        initial_line = initial_line[entry_start + len(delimiter):]
        entry_start: int = offset + entry_start + len(delimiter)

    # As an optimization against having to read more from the object,
    # perhaps our ending delimiter is also present in our initial line?
    entry_end: int = initial_line.find(delimiter, minimum_entry_size)
    if entry_end != -1:
        # We successfully found the ending delimiter from
        # within our initial line, so we are done here!
        return initial_line[:entry_end], entry_start, entry_start + entry_end

    if initial_line_length < maximum_entry_size + len(delimiter) * 2:
        # We have encountered an end of file! This implies that what
        # we have so far is as much as we are going to get.
        return initial_line, entry_start, entry_start + len(initial_line)

    # We already captured an initial segment of our data,
    # so let's try not to read more than we have to here!
    # We do not include the delimiter size here because
    # our initial line read took care of those bytes.
    ending_line = obj.read(max(maximum_entry_size - len(initial_line) + len(delimiter), 0))

    # Our minimum entry size means that we might be able
    # to skip over some bytes for finding the delimiter!
    # However, some of our "minimum" bytes can be captured
    # as part of our initial line read.
    entry_end: int = ending_line.find(
        delimiter, max(minimum_entry_size - len(initial_line), 0))

    if entry_end == -1:
        if len(ending_line) < maximum_entry_size - len(initial_line) + len(delimiter):
            # We failed to locate the ending delimiter; however,
            # that is because we have encountered the end of the
            # file, which we will treat as if the end instead.
            combined_content: bytes = initial_line + ending_line
            return combined_content, entry_start, entry_start + len(combined_content)
        else:
            raise RuntimeError(f"Failed to locate entry end delimiter for offset {offset!s}")

    combined_content: bytes = initial_line + ending_line[:entry_end]
    return combined_content, entry_start, entry_start + len(combined_content)


def get_entry_at(
        obj: BinaryIO,
        offset: int,
        minimum_entry_size: int = 1,
        maximum_entry_size: int = 128,
        delimiter: bytes = b"\n"
) -> tuple[bytes, int, int]:
    """
    Find an entry containing a file offset

    Do not use this function if an entry present at an exact offset
    is not necessary as this will cause potentially many unnecessary
    file reads to locate the desired entry. See get_entry. This
    function is a wrapper around it to provide entries at exact offsets.

    Args:
        obj: A file-like object opened in binary mode.
        offset: Byte offset in the file to start searching.
        minimum_entry_size: Minimum number of bytes an entry includes.
        maximum_entry_size: Maximum number of bytes an entry includes.
        delimiter: A single byte delimiter that delimits entries.

    Returns:
        tuple[bytes, int, int]: A tuple containing:
            - The extracted entry as bytes (excluding delimiters).
            - The starting byte index of the entry within the file.
            - The ending byte index of the entry within the file.

    Raises:
        RuntimeError: If the starting or ending delimiter cannot
            be found within the read limits.
    """

    # The get_entry function returns an entry where the
    # delimiter starts at the offset or later, whereas
    # in this case, we desire the entry that exists at
    # an index. As a result, we retrieve an initial
    # entry based on our available heuristics and
    # "walk up" to our true desired entry.
    # fmt: off
    initial_content, initial_start, initial_end = get_entry(
        obj, max(offset - maximum_entry_size - len(delimiter), 0),
        minimum_entry_size, maximum_entry_size, delimiter
    )

    # Check if our initial entry is our desired entry
    if initial_start <= offset <= initial_end:
        return initial_content, initial_start, initial_end

    # We have now established a baseline! Time to "walk up"
    # to our desired entry given our starting point.
    while True:
        # fmt: off
        initial_content, initial_start, initial_end = get_entry(
            obj, initial_end, minimum_entry_size, maximum_entry_size, delimiter
        )

        if initial_start <= offset <= initial_end:
            return initial_content, initial_start, initial_end

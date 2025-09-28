"""
Locate entries within a file-like object

Utilities to identify an entry within a file-like object,
meant for situations where entries are not of an exact
size and retrieving an exact entry is not necessary.
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
    Find an entry encased in a delimiter starting at an offset

    Entries are expected to both begin and end with the delimiter.

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
    current_position: int = obj.seek(offset)

    # Read the content at our offset, up to the maximum entry size in bytes
    line_content: bytes = obj.read(maximum_entry_size)

    # Find our starting delimiter, except if our offset is 0, it is 0
    instance_location: int = line_content.find(delimiter) if offset > 0 else 0
    if instance_location == -1:
        raise RuntimeError("Failed to locate initial delimiter")

    # We already have some content, so let's see if we can find our ending
    # delimiter with what we have to prevent another file read! We can
    # skip a few bytes during iteration given we know the minimum entry size.
    end_instance_location: int = line_content.find(
        delimiter, instance_location + minimum_entry_size
    )
    if end_instance_location != -1:
        # We found our end location without having to do an additional read!
        # This means we have identified both the start and end offsets.
        entry_start_index: int = current_position + instance_location + 1
        entry_end_index: int = current_position + end_instance_location

        # fmt: off
        return (
            line_content[instance_location + 1: end_instance_location],
            entry_start_index, entry_end_index,
        )

    # Continue where we left off; however, we can intelligently decide
    # how many bytes to read as we already have a substring of content.
    # Hence, our maximum number of bytes to read is our maximum entry
    # size reduced by the number of bytes we already read.
    end_line_content: bytes = obj.read(
        maximum_entry_size - len(line_content) + instance_location
    )

    # Locate our end delimiter with the assumption that the file always ends
    # with one. We can also skip a few bytes knowing our minimum entry size
    # again; however, we can't always skip here given that the bytes
    # corresponding to those could be held in our line_content buffer.
    end_instance_location: int = end_line_content.find(
        delimiter, max(minimum_entry_size - len(line_content) + instance_location, 0)
    )
    if end_instance_location == -1:
        raise RuntimeError("Failed to locate end delimiter")

    # We have now located and read both our start and end!
    entry_start_index: int = current_position + instance_location + 1
    entry_end_index: int = current_position + maximum_entry_size + end_instance_location

    # fmt: off
    return (
        line_content[instance_location + 1:] + end_line_content[:end_instance_location],
        entry_start_index, entry_end_index,
    )

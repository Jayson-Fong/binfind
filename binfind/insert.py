import math
import os
from typing import BinaryIO

import binfind.util
from binfind import search


def insert_fixed_key_entry(
        obj: BinaryIO,
        key: bytes,
        value: bytes,
        minimum_entry_size: int | None = None,
        maximum_entry_size: int = 128,
        delimiter: bytes = b"\n",
        chunk_size: int = 1024 * 1024,
        start_index: int = 0,
        end_index: int | None = None,
):
    """
    Insert an entry into a buffer.

    This function assumes that keys are of a fixed length and
    all values existing within the table conform to this standard.

    Args:
        obj: Buffer capable of read and write operations.
        key: Key to insert.
        value: Value to insert.
        minimum_entry_size: Minimum length of entries in bytes, used as a heuristic.
        maximum_entry_size: Maximum length of entries in bytes, used as a heuristic.
        delimiter: Delimiter between entries.
        chunk_size: Number of bytes to shift at a time.
        start_index: Offset to start searching at.
        end_index: Offset to stop searching at.

    Returns:

    """

    if minimum_entry_size is None or minimum_entry_size < len(key):
        minimum_entry_size: int = len(key)

    if len(key) + len(value) > maximum_entry_size:
        raise ValueError("The key length may not exceed the maximum entry size")

    obj.seek(0, os.SEEK_END)
    obj_end_index: int = obj.tell()
    if end_index is None:
        end_index: int = obj_end_index

    if start_index == obj_end_index or obj_end_index == 0:
        if start_index == 0:
            # The file is empty. We can write immediately. There
            # is no delimiter required because the start and
            # end are interpreted as delimiters.
            obj.seek(0, os.SEEK_SET)
            obj.write(key + value)

            return 0, len(key) + len(value)

        obj.seek(start_index, os.SEEK_SET)
        obj.write(delimiter + key + value)

        return start_index + len(delimiter), start_index + len(key) + len(value) + len(delimiter)

    while start_index < end_index - len(delimiter):
        search_value, search_start, search_end = search.get_entry_at(
            obj, math.floor((start_index + end_index) / 2),
            minimum_entry_size=minimum_entry_size,
            maximum_entry_size=maximum_entry_size,
            delimiter=delimiter,
        )

        search_key: bytes = search_value[:len(key)]
        if search_key == key:
            start_index: int = search_end
            break
        elif search_key > key:
            end_index = search_start
        else:
            start_index = search_end

    if start_index == 0:
        binfind.util.space(obj, offset=0, length=len(key) + len(value) + len(delimiter), chunk_size=chunk_size)
        obj.seek(start_index, os.SEEK_SET)
        obj.write(key + value + delimiter)
        return start_index, start_index + len(key) + len(value)

    binfind.util.space(obj, offset=start_index, length=len(key) + len(value) + len(delimiter), chunk_size=chunk_size)
    obj.seek(start_index, os.SEEK_SET)
    obj.write(delimiter + key + value)
    return start_index + len(delimiter), start_index + len(key) + len(value) + len(delimiter)

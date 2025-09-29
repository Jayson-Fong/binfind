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
):
    # This method assumes that the key is of a fixed
    # length and all values already existing conform
    # to this standard.
    if minimum_entry_size is None or minimum_entry_size < len(key):
        minimum_entry_size: int = len(key)

    if len(key) + len(value) > maximum_entry_size:
        raise ValueError("The key length may not exceed the maximum entry size")

    # To acquire the file size, seek the end
    obj.seek(0, os.SEEK_END)
    start_index: int = 0
    end_index: int = obj.tell()

    last_key: bytes | None = None
    last_location: tuple[int | None, int | None] = None, None
    while True:
        # Roughly compute the middle and derive the entry for it
        search_value, search_start, search_end = search.get_entry_at(
            obj, math.floor((start_index + end_index) / 2),
            minimum_entry_size=minimum_entry_size,
            maximum_entry_size=maximum_entry_size,
            delimiter=delimiter,
        )

        if (search_start, search_end) == last_location:
            break

        last_key: bytes = search_value[:len(key)]
        last_location = (search_start, search_end)
        if last_key == key:
            start_index = search_start
            end_index: int = search_start - len(delimiter) if search_start > 0 else 0
        elif last_key < key:
            # Our desired position is to the right!
            start_index: int = search_end
        elif last_key > key:
            # Our desired position is to the left!
            end_index: int = search_start - len(delimiter) if search_start > 0 else 0

    # We have deduced the location of an entry that's just about
    # where we want to insert, but not quite yet! We need to
    # determine the exact location ourselves on whether we want
    # to insert before or after the identified entry.
    if key < last_key:
        # Insert before
        binfind.util.space(
            obj, offset=last_location[0],
            length=len(key) + len(value) + len(delimiter), chunk_size=chunk_size)
        obj.seek(last_location[0], os.SEEK_SET)
        obj.write(key + value + delimiter)
    else:
        binfind.util.space(
            obj, offset=last_location[1],
            length=len(key) + len(value) + len(delimiter), chunk_size=chunk_size)
        obj.seek(last_location[1])
        obj.write(delimiter + key + value)

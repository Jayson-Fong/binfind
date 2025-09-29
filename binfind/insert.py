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

    if end_index == 0:
        # The file is empty. We can write immediately. There
        # is no delimiter required because the start and
        # end are interpreted as delimiters.
        obj.seek(0, os.SEEK_SET)
        obj.write(key + value)
        return

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
        binfind.util.space(obj, offset=0, length=len(key) + len(value) + len(delimiter))
        obj.seek(start_index, os.SEEK_SET)
        obj.write(key + value + delimiter)
        return

    binfind.util.space(obj, offset=start_index, length=len(key) + len(value) + len(delimiter))
    obj.seek(start_index, os.SEEK_SET)
    obj.write(delimiter + key + value)

import os
from typing import BinaryIO


def space(obj: BinaryIO, offset: int, length: int, chunk_size: int = 1024 * 1024):
    obj.seek(0, os.SEEK_END)
    end_position: int = obj.tell()

    if offset == end_position:
        return

    # Shift the data
    for pos in range(end_position, offset, -chunk_size):
        read_start = max(offset, pos - chunk_size)

        obj.seek(read_start)
        chunk = obj.read(min(chunk_size, end_position - read_start))

        obj.seek(read_start + length)
        obj.write(chunk)

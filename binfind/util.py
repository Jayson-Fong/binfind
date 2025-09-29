import os
from typing import BinaryIO


def space(obj: BinaryIO, offset: int, length: int, chunk_size: int = 1024 * 1024):
    # Extend the file
    obj.seek(0, os.SEEK_END)
    end_position: int = obj.tell()
    obj.truncate(end_position + length)

    # Shift the data
    for pos in range(end_position, offset, -chunk_size):
        read_start = max(offset, pos - chunk_size)

        obj.seek(read_start)
        chunk = obj.read(min(chunk_size, end_position - read_start))

        obj.seek(read_start + length)
        obj.write(chunk)

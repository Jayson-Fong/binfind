import os
from typing import BinaryIO


def space(obj: BinaryIO, offset: int, length: int, chunk_size: int = 1024 * 1024):
    # Extend the file
    obj.seek(0, os.SEEK_END)
    end_position: int = obj.tell()
    obj.truncate(end_position + length)

    # Shift the data
    for pos in range(end_position - 1, offset - 1, -1):
        obj.seek(pos, os.SEEK_SET)
        chunk: bytes = obj.read(1)

        obj.seek(pos + length, os.SEEK_SET)
        obj.write(chunk)

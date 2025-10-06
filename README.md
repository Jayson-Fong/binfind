binfind
=======

Locates a record within a binary file given variable length records.

# Purpose
This program is specifically designed with large lookup tables in mind, optimizing for memory and disk space while 
maintaining human readability. This package is **not** meant to enable access to file content by line numbers 
(see [linecache](https://docs.python.org/3/library/linecache.html) instead), but file offsets.

This program is currently **not** a good candidate if you need to insert many entries at once as the program will 
repeatedly perform disk I/O for each entry. This will likely be addressed in a future release for _small datasets that 
can fit in memory_.

Usage of this package heavily relies on heuristics to enable efficient I/O at scale, such as information about the size
of entries and rough offset ranges of where a desired entry is or should be.
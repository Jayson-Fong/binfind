binfind
=======

Locates a record within a binary file given variable length records.

# Purpose
This program is specifically designed with large lookup tables in mind, optimizing for memory, disk reads, and CPU. This
package is **not** meant to enable access to file content by line numbers 
(see [linecache](https://docs.python.org/3/library/linecache.html) instead), but file offsets.

This program is currently **not** a good candidate if you need to insert many entries at once as the program will 
repeatedly perform disk I/O for each entry. This will likely be addressed in a future release for _small datasets that 
can fit in memory_. At this time, you can expect that inserting many entries individually on a modern CPU may spend over
70% of the time merely shifting data to insert in the middle of a file.
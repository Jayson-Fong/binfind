binfind
=======

Locates a record within a binary file given variable length records.

# Purpose
This program is specifically designed with large lookup tables in mind, optimizing for memory, disk reads, and CPU. This
package is **not** meant to enable access to file content by line numbers 
(see [linecache](https://docs.python.org/3/library/linecache.html) instead), but file offsets.

# Known issues
- `binfind.insert.insert_fixed_key_entry` does not properly handle starting a file (one without any existing entries)
- `binfind.util.space` is unnecessarily inefficient due to moving one byte at a time.

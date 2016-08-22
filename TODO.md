* Make `Command` more resilient to non-compiling invocations. For example:
    * `gcc --help`
    * `gcc ... file1.c file2.c ...`
* Limit `.define-query` blocks to one-at-a-time. That is, allow the `.query` 
  attribute of `.define-plot` to refer only to the most recently encountered
  `.define-query`. This way, the parser need only keep track of one (any
  constant would do, but one seems most natural) query -- this allows an
  infinite number of plot descriptions to be streamed into the report
  generator while using only a fixed amount of memory.
* Write tools for splitting and recombining the database. After a while, the
  sqlite3 database will become very large on the disk. A tool that takes all
  `Compilation` records older than a certain date (along with any foreign
  records from other tables exclusive to `Compilation` records from the era)
  and writes them to a new database, erasing the records in the original
  database. Then later, if necessary, another tool can be used to recombine
  any number of such split databases.
* Add a "when was this generated" image to the output of report generation so
  that report markdown authors can refer to the image to stamp their report
  when generated.

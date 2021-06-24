
from __future__ import print_function

fileDef = '''
create table if not exists
File(
    Key         integer primary key,
    Name        text not null,
    Path        text not null,
    GitRevision text not null, /* empty string if not available */
    GitDiffHead text not null,
    LineCount integer,
    SizeBytes integer,
    PreprocessedSizeBytes integer,
    PreprocessedLineCount integer,

    unique(Name, Path, GitRevision, GitDiffHead, SizeBytes)
);'''

machineDef = '''
create table if not exists
Machine(
    Key         integer primary key,
    Name        text not null,
    System      text not null,
    Release     text not null,
    Version     text not null,
    MachineArch text not null,
    Processor   text not null,
    PageSize    integer not null,

    unique(Name, System, Release, Version, MachineArch, Processor,
           PageSize)
);'''

compilationDef = '''
create table if not exists 
Compilation(
    Key                      text primary key,
    User                     text not null,
    StartIso8601             text not null,
    DurationSeconds          real not null,
    MaxResidentMemoryBytes   integer not null,
    UserCpuTime              real not null,
    SystemCpuTime            real not null,
    BlockingInputOperations  integer not null,
    BlockingOutputOperations integer not null,
    FileKey                  integer references File(Key) not null,
    CompilerPath             text not null,
    OutputObjectSizeBytes    integer not null,
    MachineKey               integer references Machine(Key) not null
);'''

argumentDef = '''
create table if not exists
Argument(
    CompilationKey text references Compilation(Key) not null,
    Position       integer not null,
    Value          text not null,

    primary key(CompilationKey, Position)
);'''

definitions = [fileDef, machineDef, compilationDef, argumentDef]

def createAll(db):
    for table in definitions:
        db.execute(table)
    db.commit()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        sys.exit() # No output file

    import sqlite3
    db = sqlite3.connect(sys.argv[1])
    createAll(db)
    db.commit()

'''
Copyright (c) 2016 David Goffredo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

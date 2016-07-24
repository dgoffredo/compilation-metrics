
from __future__ import print_function

fileDef = '''
create table if not exists
File(
    Key         integer primary key,
    Name        text not null,
    GitRevision text,
    GitDiffHead text
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
    PageSize    integer not null
);'''

compilationDef = '''
create table if not exists 
Compilation(
    Key                      text primary key,
    StartIso8601             text not null,
    DurationSeconds          real not null,
    MaxResidentMemoryBytes   integer,
    UserCpuTime              real,
    SystemCpuTime            real,
    BlockingInputOperations  integer,
    BlockingOutputOperations integer,
    FileKey                  integer references File(Key) not null,
    OutputObjectSizeBytes    integer not null,
    MachineKey               integer references Machine(Key) not null
);'''

argumentDef = '''
create table if not exists
Argument(
    CompilationKey text references Compilation(Key) not null,
    Value          text not null
);'''

definitions = [fileDef, machineDef, compilationDef, argumentDef]

def createAll(db):
    for table in definitions:
        db.execute(table)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        sys.exit() # No output file

    import sqlite3
    db = sqlite3.connect(sys.argv[1])
    createAll(db)
    db.commit()

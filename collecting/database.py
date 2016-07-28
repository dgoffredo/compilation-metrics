
from __future__ import print_function

import os
import sys
import tables
import sqlite3
import uuid

_dbEnvKey = 'COMPILATION_METRICS_DB'

def _getDbPath(dbPath):
    if dbPath:
        return dbPath

    dbPath = os.environ.get(_dbEnvKey)
    if dbPath is None:
        raise Exception('No database name specified, and the environment '
                        'variable {} is not set.'.format(_dbEnvKey))
    return dbPath

def connect(dbPath=None):
    db = sqlite3.connect(_getDbPath(dbPath))
    tables.createAll(db)
    return db
#
# The arguments sourceFileInfo, machineInfo, and resourceInfo are dicts:
#
# sourceFileInfo keys: ['name', 'path', 'gitRevision', 'gitDiffHead']
#
# machineInfo keys: ['name', 'system', 'release', 'version', 'machineArch',
#                    'processor, 'pageSize']
#
# resourceInfo keys: ['maxResidentMemoryBytes', 'userCpuTime', 
#                     'systemCpuTime', 'blockingInputOperations',
#                     'blockingOutputOperations']
#
def createEntry(db, user, startDatetime, durationSeconds, outputObjectSizeBytes,
                sourceFileInfo, machineInfo, resourceInfo, compilerPath,
                command):
    db.execute("PRAGMA foreign_keys = ON;")

    machineKey = _addMachine(db, **machineInfo)
    fileKey = _addSourceFile(db, **sourceFileInfo)
    compilationKey = _addCompilation(db, user, startDatetime, durationSeconds,
                                     outputObjectSizeBytes, fileKey, machineKey,
                                     compilerPath, **resourceInfo)
    _addArguments(db, compilationKey, command)
    db.commit()

def _addArguments(db, compilationKey, command):
    db.executemany("insert into Argument(CompilationKey, Position, Value) "
                   "values(?, ?, ?);",
                   ((compilationKey, i, arg) for i, arg in enumerate(command))) 

def _insert(db, table, columnToValue):
    template = "insert into {table}({cols}) values({placeholders});"
    query = template.format(table=table, cols=', '.join(columnToValue.keys()),
                            placeholders=', '.join('?' for _ in columnToValue))
    db.execute(query, columnToValue.values())

def _didInsert(db, table, columnToValue):
    try:
        _insert(db, table, columnToValue)
        return True
    except sqlite3.Error as error:
        print(error, file=sys.stderr)
        return False

def _addCompilation(db, user, startDatetime, durationSeconds,
                    outputObjectSizeBytes, fileKey, machineKey, compilerPath,
                    maxResidentMemoryBytes, userCpuTime, systemCpuTime,
                    blockingInputOperations, blockingOutputOperations):
    maxAttempts = 5
    for _ in range(maxAttempts):
        key = uuid.uuid4().hex
        if _didInsert(db, 'Compilation', {
            'Key':                      key,
            'User':                     user,
            'StartIso8601':             startDatetime.isoformat(),
            'DurationSeconds':          durationSeconds,
            'OutputObjectSizeBytes':    outputObjectSizeBytes,
            'FileKey':                  fileKey,
            'MachineKey':               machineKey,
            'CompilerPath':             compilerPath,
            'MaxResidentMemoryBytes':   maxResidentMemoryBytes,
            'UserCpuTime':              userCpuTime,
            'SystemCpuTime':            systemCpuTime,
            'BlockingInputOperations':  blockingInputOperations,
            'BlockingOutputOperations': blockingOutputOperations
        }):
            return key

    msg = 'Unable to insert record after {} attempts.'.format(maxAttempts)
    raise Exception(msg)

def _addUniqueRecord(db, table, columns, values, keyColumn='Key'):
    colsStr = ', '.join(columns)
    refs = ', '.join('?' for _ in columns)
    template = "insert or ignore into {table}({cols}) values({refs});"

    db.execute(template.format(table=table, cols=colsStr, refs=refs),
               values)

    pred = ' and '.join(col + ' is ?' for col in columns)
    template = "select {keyCol} from {table} where {pred};"

    c = db.execute(template.format(keyCol=keyColumn, table=table, pred=pred),
                   values)
    
    results = list(c)
    assert len(results) == 1, "Bad insert or uniqueness constraint?"
    assert len(results[0]) == 1, "Wrong number of columns returned."
    
    return results[0][0]

def _addSourceFile(db, name, path, gitRevision, gitDiffHead):
    columns = ['Name', 'Path', 'GitRevision', 'GitDiffHead']
    values = (name, path, gitRevision, gitDiffHead)

    return _addUniqueRecord(db, 'File', columns, values)

def _addMachine(db, name, system, release, version, machineArch, processor,
                pageSize):
    columns = ['Name', 'System', 'Release', 'Version', 'MachineArch', 
               'Processor', 'PageSize']
    values = (name, system, release, version, machineArch, processor, pageSize)

    return _addUniqueRecord(db, 'Machine', columns, values)

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

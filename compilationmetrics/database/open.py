
from __future__ import print_function

import os
import sqlite3
import datetime

import tables

sqlite3.register_adapter(datetime.datetime, datetime.datetime.isoformat)

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
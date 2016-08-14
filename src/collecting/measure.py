
from __future__ import print_function

# Measure resources used by a subprocess. This module assumes that the
# command to be measured will result in the first measurable usage of
# resources by any child process. This practically means that you can
# measure only once, and that you must do so before having created any
# child processes.

import resource
import subprocess
import time
import datetime

utcnow = datetime.datetime.utcnow

# resourceInfo keys: ['maxResidentMemoryBytes', 'userCpuTime', 
#                     'systemCpuTime', 'blockingInputOperations',
#                     'blockingOutputOperations']

def childrenUsage():
    data = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {
        'userCpuTime': data.ru_utime,
        'systemCpuTime': data.ru_stime,
        'maxResidentMemoryBytes': data.ru_maxrss * 1024,
        'blockingInputOperations': data.ru_inblock,
        'blockingOutputOperations': data.ru_oublock
    }

# Returns (returnCode, startDatetime, wallTimeDurationSeconds, ResourceUsage)
#
def call(command):
    before = childrenUsage()
    assert all(val == 0 for val in before.itervalues()), 'Not your first child.'

    start = utcnow()
    rc = subprocess.call(command)
    duration = (utcnow() - start).total_seconds()
    return rc, start, duration, childrenUsage()

if __name__ == '__main__':
    import sys
    rc, start, duration, usage = call(sys.argv[1:])
    print('return code:', rc)
    print('start:', start)
    print('duration:', duration, 'seconds')
    print('usage:', usage)

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

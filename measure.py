
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

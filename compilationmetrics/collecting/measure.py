# Measure resources used by a subprocess.
#
# This module uses a helper executable, `measure`, expected to be in the same
# directory as this script.  The repository's `Makefile` compiles the helper.

from ..enforce import enforce

import datetime
import json
import os
from pathlib import Path
import subprocess
import time

utcnow = datetime.datetime.utcnow
measure_exe = Path(__file__).resolve().parent/'measure'

def timeval_to_seconds(timeval):
    sec, usec = timeval['tv_sec'], timeval['tv_usec']
    return sec + usec / 1000000

def formatUsage(data):
    return {
        'userCpuTime': timeval_to_seconds(data['ru_utime']),
        'systemCpuTime': timeval_to_seconds(data['ru_stime']),
        'maxResidentMemoryBytes': data['ru_maxrss'] * 1024,
        'blockingInputOperations': data['ru_inblock'],
        'blockingOutputOperations': data['ru_oublock']
    }

# Returns (returnCode, startDatetime, wallTimeDurationSeconds, ResourceUsage)
#
def call(command):
    # Run the command in a wrapper (`measure_exe`).  The wrapper takes an
    # argument naming a file descriptor that it will write the resource usage
    # to as JSON.
    #
    # We give it the write end of a pipe created using `os.pipe()`.  We'll read
    # from the read end.  We have to include the write end among the file
    # descriptors to "pass" (i.e. _not_ close) to the child process.
    #
    # Also, we have to close _our_ version of the write end of the pipe once
    # the child process has its version.  This way, when we read from the read
    # end, the only open writer is the child process's.  Were we to keep ours
    # open, `.read()` would block indefinitely.
    #
    # Once we've read all the data from the pipe and the child process has
    # terminated, parse the data from JSON and massage it for returning to
    # the caller (see `formatUsage`).
    #
    # Separately, keep track of the total wall time taken by the child process.

    pipe_read_end, pipe_write_end = os.pipe()
    command = [measure_exe, f'fd://{pipe_write_end}', *command]
    start = utcnow()
    child = subprocess.Popen(command, pass_fds=(pipe_write_end,))
    os.close(pipe_write_end) # so that only the child's copy of the fd is open
    rusage_json = os.fdopen(pipe_read_end).read()
    rc = child.wait()
    duration = (utcnow() - start).total_seconds()
    rusage_dict = json.loads(rusage_json)
    return rc, start, duration, formatUsage(rusage_dict)

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

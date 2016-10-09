
from __future__ import print_function

import command
import git
import measure

import sys
import platform
import resource
import os
import getpass
import traceback

def _machineInfo():
    uname = platform.uname()
    return {
        'system': uname[0],
        'name': uname[1],
        'release': uname[2],
        'version': uname[3],
        'machineArch': uname[4],
        'processor': uname[5],
        'pageSize': resource.getpagesize()
    }

def _writeToDatabaseImpl(user, startDatetime, durationSeconds, outputSizeBytes,
                        sourceInfo, machineInfo, resources, compilerPath,
                        command):
    # Delay importing 'database.write', because it imports 'uuid', which forks
    # the process, which throws off the "children" resource consumption
    # measurements. At this point, though, we're done measuring, so another
    # fork is fine.
    #
    from ..database.open import connect
    from ..database.write import createEntry

    db = connect()
    createEntry(db, user, startDatetime, durationSeconds,
                outputSizeBytes, sourceInfo, machineInfo, resources,
                compilerPath, command)

def writeToDatabase(request):
    return _writeToDatabaseImpl(**request)

def _doMetrics(cmd, start, durationSeconds, resources, callback):
    sourcePath, outputPath, compilerPath, error = cmd.getPaths()
    if error:
        return # TODO: In verbose mode, display why.

    source = os.path.basename(sourcePath)
    outputSize = os.path.getsize(outputPath)

    if git.hasGit() and git.inAnyRepo(sourcePath):
        revision = git.getHeadRevision(sourcePath)
        diff = git.diffHead(sourcePath)
    else:
        revision = ''
        diff = ''

    sourceInfo = {
        'name': source,
        'path': sourcePath,
        'gitRevision': revision,
        'gitDiffHead': diff
    }

    request = {
        'user': getpass.getuser(),
        'startDatetime': start.isoformat(),
        'durationSeconds': durationSeconds,
        'outputSizeBytes': outputSize,
        'sourceInfo': sourceInfo,
        'machineInfo': _machineInfo(),
        'resources': resources,
        'compilerPath': compilerPath,
        'command': cmd
    }

    callback(request)

def collect(args, callback=writeToDatabase, debug=False):
    cmd = command.Command(args)
    if len(cmd) == 0:
        return 0 # Nothing to do

    rc, start, durationSeconds, resources = measure.call(cmd)
    if rc != 0:
        return rc # Compilation failed, so there's nothing to do.

    try:
        _doMetrics(cmd, start, durationSeconds, resources, callback)
    except Exception:
        if debug:
            traceback.print_exc(file=sys.stderr)

    # Always return the result of 'measure.call', so that even if recording
    # compilation metrics fails, this script continues to act as a pass-though
    # to the compiler.
    #
    return rc

if __name__ == '__main__':
    sys.exit(collect(sys.argv[1:]))


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

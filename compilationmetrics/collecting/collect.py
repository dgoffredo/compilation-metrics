
from __future__ import print_function

import command
import git
import measure

import sys 
import platform
import resource
import os
import getpass

def machineInfo():
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

def doMetrics(cmd, start, durationSeconds, resources):
    sourcePath = cmd.sourcePath()
    source = os.path.basename(sourcePath)
    outputSize = os.path.getsize(cmd.outputPath())
    compilerPath = cmd.compilerPath()

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

    # Delay importing 'database.write', because it imports 'uuid', which forks
    # the process, which throws off the "children" resource consumption
    # measurements. At this point, though, we're done measuring, so another
    # fork is fine.
    #
    from ..database.open import connect
    from ..database.write import createEntry

    db = connect()
    createEntry(db, getpass.getuser(), start, durationSeconds,
                outputSize, sourceInfo, machineInfo(), resources,
                compilerPath, cmd)

def collect(args):
    cmd = command.Command(args)
    rc, start, durationSeconds, resources = measure.call(cmd)
    if rc != 0:
        return rc # Compilation failed, so there's nothing to do.

    try:
        doMetrics(cmd, start, durationSeconds, resources)
        # TODO: It ought not to be a reportable error if the Command doesn't
        #       have the info we want. Reportable errors should be things like
        #       the database not being available, etc.
    except Exception as error:
        print('An Exception occurred while doing metrics:', error,
              file=sys.stderr)

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

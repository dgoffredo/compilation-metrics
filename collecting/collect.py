
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
        'name': uname[0],
        'system': uname[1],
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

    if git.inAnyRepo(sourcePath):
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

    # Delay importing 'database', because it imports 'uuid', which forks
    # the process, which throws off the "children" resource consumption
    # measurements. At this point, though, we're done measuring, so another
    # fork is fine.
    #
    import database

    db = database.connect()
    database.createEntry(db, getpass.getuser(), start, durationSeconds,
                         outputSize, sourceInfo, machineInfo(), resources,
                         compilerPath, cmd)

def collect(args):
    cmd = command.Command(args)
    rc, start, durationSeconds, resources = measure.call(cmd)
    if rc != 0:
        return rc # Compilation failed, so there's nothing to do.

    try:
        doMetrics(cmd, start, durationSeconds, resources)
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


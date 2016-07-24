
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
    pass # TODO: Rename fields from platform.uname
    # ['name', 'system', 'release', 'version', 'machineArch',
    #  'processor, 'pageSize']
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
    # the process, which throws of the "children" resource consumption
    # measurements. At this point, though, we're done measuring, so another
    # fork is fine.
    #
    import database

    db = database.connect()
    database.createEntry(db, getpass.getuser(), start, durationSeconds,
                         outputSize, sourceInfo, machineInfo(), resources, cmd)

if __name__ == '__main__':

    cmd = command.Command(sys.argv[1:])

    rc, start, durationSeconds, resources = measure.call(cmd)

    if rc != 0:
        sys.exit(rc) # Compilation succeed, so there's nothing to do.

    try:
        doMetrics(cmd, start, durationSeconds, resources)
    except Exception as error:
        print('An Exception occurred while doing metrics:', error)

    sys.exit(rc) # Always return the result of 'measure.call'

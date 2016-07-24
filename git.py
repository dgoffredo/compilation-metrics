
from __future__ import print_function

import subprocess
import os

def _dirOf(filePath):
    return os.path.dirname(os.path.realpath(filePath))

# Returns (returnCode, stdout)
# where stdout is stripped of trailing whitespace.
#
def _callInDirOf(filePath, command):
    with open(os.devnull, 'wb') as devnull:
        process = subprocess.Popen(command,
                                   cwd=_dirOf(filePath),
                                   stdout=subprocess.PIPE,
                                   stderr=devnull)
        output, _ = process.communicate()
        return process.returncode, output.rstrip()

def inAnyRepo(filePath):
    rc, _ = _callInDirOf(filePath, ['git', 'rev-parse'])
    return rc == 0

def getHeadRevision(filePath):
    rc, output = _callInDirOf(filePath, ['git', 'rev-parse', 'HEAD'])
    assert rc == 0, "Can't get revision. Is {} in a git repo?".format(filePath)
    return output

def diffHead(filePath):
    rc, output = _callInDirOf(filePath, 
                              ['git', 'diff', os.path.basename(filePath)])
    assert rc == 0, "Can't diff file. Is {} in a git repo?".format(filePath)
    return output

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        sys.exit() # Nothing to do

    filePath = sys.argv[1]
    isInGit = inAnyRepo(filePath)
    print('In git repository? ', 'True' if isInGit else 'False')
    if isInGit:
        print('Head revision: ', getHeadRevision(filePath))
        print('Diff with HEAD: \n', diffHead(filePath))

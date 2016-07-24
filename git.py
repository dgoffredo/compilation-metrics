
from __future__ import print_function

import subprocess
import os

def _dirOf(filePath):
    return os.path.dirname(os.path.realpath(filePath))

def inAnyRepo(filePath):
    return 0 == subprocess.call(['git', 'rev-parse'],
                                cwd=_dirOf(filePath),
                                stdout=os.devnull, 
                                stderr=devnull)

def getHeadRevision(filePath):
    pass # TODO

def diffHead(filePath):
    pass # TODO

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        sys.exit() # Nothing to do

    filePath = argv[1]
    isInGit = inAnyRepo(filePath)
    print('In git repository? ', 'True' if isInGit else 'False')
    if isInGit:
        print('Head revision: ', getHeadRevision(filePath))
        print('Diff with HEAD: \n', diffHead(filePath))

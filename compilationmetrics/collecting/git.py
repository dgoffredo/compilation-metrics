from ..enforce import enforce

import subprocess
import os
from distutils.spawn import find_executable


def _dirOf(filePath):
    return os.path.dirname(os.path.realpath(filePath))


# Returns (returnCode, stdout)
# where stdout is stripped of trailing whitespace.
#
def _callInDirOf(filePath, command):
    with open(os.devnull, 'wb') as devnull:
        process = subprocess.Popen(command,
                                   encoding='utf8',
                                   cwd=_dirOf(filePath),
                                   stdout=subprocess.PIPE,
                                   stderr=devnull)
        output, _ = process.communicate()
        return process.returncode, output.rstrip()


def hasGit():
    return find_executable('git') is not None


def inAnyRepo(filePath):
    rc, _ = _callInDirOf(filePath, ['git', 'rev-parse'])
    return rc == 0


def getHeadRevision(filePath):
    rc, output = _callInDirOf(filePath, ['git', 'rev-parse', 'HEAD'])
    enforce(rc == 0,
            "Can't get revision. Is {} in a git repo?".format(filePath))
    return output


def diffHead(filePath):
    rc, output = _callInDirOf(
        filePath, ['git', 'diff', os.path.basename(filePath)])
    enforce(rc == 0, "Can't diff file. Is {} in a git repo?".format(filePath))
    return output


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        sys.exit()  # Nothing to do

    filePath = sys.argv[1]
    isInGit = inAnyRepo(filePath)
    print('In git repository? ', 'True' if isInGit else 'False')
    if isInGit:
        print('Head revision: ', getHeadRevision(filePath))
        print('Diff with HEAD: \n', diffHead(filePath))
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

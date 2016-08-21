
from distutils.spawn import find_executable
from contextlib import contextmanager
import subprocess
import os.path

def hasPerl():
    return find_executable('perl') is not None

@contextmanager
def _openedFile(fileOrPath):
    if isinstance(fileOrPath, basestring):
        with open(fileOrPath) as file:
            yield file
    else:
        yield fileOrPath # Assume we already have a file.

def _moduleDirectory():
    return os.path.dirname(os.path.realpath(__file__))

def _scriptPath():
    return os.path.join(_moduleDirectory(), 'Markdown.pl')

def _renderHtml(source, destination):
    return subprocess.call(['perl', _scriptPath()], 
                            stdin=source,
                            stdout=destination)

def toHtml(sourceFileOrPath, destinationFileOrPath):
    assert hasPerl(), 'Markdown rendering requires perl.'
    with _openedFile(sourceFileOrPath) as source:
        with _openedFile(destinationFileOrPath) as destination:
            _renderHtml(source, destination)

if __name__ == '__main__':
    from sys import argv, stdin, stdout
    assert len(argv) <= 2, 'Specify zero or one input file.'
    
    if len(argv) == 2:
        toHtml(argv[1], stdout)
    else:
        toHtml(stdin, stdout)
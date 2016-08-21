
from __future__ import print_function
from distutils.spawn import find_executable
import subprocess
import os
import json

def hasGnuplot():
    return find_executable('gnuplot') is not None

# Prepare for sending to gnuplot as data. Print as-is, except for strings,
# which are quoted and escaped.
def stringify(value):
    if isinstance(value, basestring):
        # quoted and escaped string
        return json.dumps(value)
    else:
        return str(value)

class Gnuplot(object):
    def __init__(self):
        assert hasGnuplot, "Can't find gnuplot."
        self._devnull = open(os.devnull, 'wb')
        self._subprocess = subprocess.Popen(['gnuplot'],
                                            stdin=subprocess.PIPE,
                                            stdout=self._devnull)
        self._stdin = self._subprocess.stdin

    def writeLine(self, text):
        self._stdin.write(text)
        if text[-1] != '\n':
            self._stdin.write('\n')

    def send(self, *lines):
        for line in lines:
            self.writeLine(line)
        self._stdin.flush()

    def reset(self):
        self.send('reset')

    def endDataSection(self):
        self.send('e')

    def writeDataRow(self, row):
        self.writeLine(' '.join(stringify(value) for value in row))

    def closeOutput(self):
        self.send("set output")

    def quit(self):
        self._stdin.close()
        self._subprocess.wait()
        self._devnull.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.quit()

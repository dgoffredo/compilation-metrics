
from distutils.spawn import find_executable
import subprocess
import os
import json

from ..enforce import enforce

def hasGnuplot():
    return find_executable('gnuplot') is not None

# Prepare for sending to gnuplot as data. Print as-is, except for strings,
# which are quoted and escaped.
def stringify(value):
    if isinstance(value, str):
        # quoted and escaped string
        return json.dumps(value)
    else:
        return str(value)

class Gnuplot(object):
    def __init__(self):
        enforce(hasGnuplot, "Can't find gnuplot.")
        self._devnull = open(os.devnull, 'wb')
        self._subprocess = subprocess.Popen(['gnuplot'],
                                            stdin=subprocess.PIPE,
                                            stdout=self._devnull)
        self._stdin = self._subprocess.stdin

    def writeLine(self, text):
        self._stdin.write(text.encode('utf8'))
        if text[-1] != '\n':
            self._stdin.write(b'\n')

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

from __future__ import print_function
import re

class TokenKind:
    EMPTY_LINE = 'EMPTY_LINE'
    COMMAND_LINE = 'COMMAND_LINE'
    INDENTED_LINE = 'INDENTED_LINE'

class Token(object):
    def __init__(self, kind, text):
        self.kind = kind
        self.text = text

    def __str__(self):
        return '<{}: "{}">'.format(self.kind, self.text.rstrip())

def indentWidth():
    return 4

class _Regex:
    empty = re.compile(r'^\s*$')
    command = re.compile(r'^\.\s*\S')
    indented = re.compile(r'^[ ]{{{}}}\s*\S'.format(indentWidth()))

def unindent(line):
    return line[indentWidth():]

# A generator :: file object --> Token
def lex(file):
    for line in file:
        if _Regex.empty.match(line):
            yield Token(TokenKind.EMPTY_LINE, line)
        elif _Regex.indented.match(line):
            yield Token(TokenKind.INDENTED_LINE, unindent(line))
        else:
            enforce(_Regex.command.match(line), 'Invalid line: {}'.format(line))
            yield Token(TokenKind.COMMAND_LINE, line)

if __name__ == '__main__':
    import sys
    for token in lex(sys.stdin):
        print(token)
            
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

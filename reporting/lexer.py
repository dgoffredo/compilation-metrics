
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
            assert _Regex.command.match(line), 'Invalid line: {}'.format(line)
            yield Token(TokenKind.COMMAND_LINE, line)

if __name__ == '__main__':
    import sys
    for token in lex(sys.stdin):
        print(token)
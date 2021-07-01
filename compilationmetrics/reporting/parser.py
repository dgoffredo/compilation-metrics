from ..enforce import enforce
'''
This parser has four states (excluding the end states "error" and "success"),
transitions among which are described below:

The following abbreviations are used for the token kinds:
    E = TokenKind.EMPTY_LINE
    C = TokenKind.COMMAND_LINE
    I = TokenKind.INDENTED_LINE

The following abbreviation is used to indicate the end of input:
    $ = End of input

State Name             Token  Next State  Note / Action
---------------------  -----  ----------  ------------------------------------
(1) Expect Definition  E      (1)         Useless whitespace outside any def
                       C      (2)         Add definition and first trait
                       I      Error       SQL must be preceded by an empty line
                       $      Success     This file was all whitespace or empty

(2) Expect Command     E      (3)         Done with def or is SQL next?
                       C      (2)         Add trait to current def
                       I      Error       SQL must be preceded by an empty line
                       $      Success     This last def had only one trait

(3) Expect Def or SQL  E      (1)         Current definition is done
                       C      (2)         Add definition and first trait
                       I      (4)         Add SQL block to current def
                       $      Success     This last def had only one trait

(4) Expect sql or end  E      (1)         Current def had a one line SQL query
                       C      Error       Need empty line between SQL and def
                       I      (4)         Adding more lines to the current SQL
                       $      Success     The last def's SQL just ended
'''

from . import lexer

Kind = lexer.TokenKind

import shlex


def _getWords(line):
    shLexer = shlex.shlex(instream=line, posix=True)
    shLexer.commenters = ''
    shLexer.wordchars += '-'
    return list(shLexer)


class Trait(object):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return '<Trait name: {} args: {}'.format(self.name, self.args)


def _parseTrait(text):
    words = _getWords(text)
    template = 'Need at least a dot, a name, and one arg. '
    template += 'Bad command: "{}" parsed as: {}'
    enforce(len(words) >= 3, template.format(text, words))
    # ['.', 'name', 'arg1', 'arg2', ...]
    #     --> Trait('name', ['arg1', 'arg2', ...])
    return Trait(name=words[1], args=words[2:])


class Definition(object):
    def __init__(self):
        self.traits = []
        self.sqlBlock = None

    def __str__(self):
        return '<definition traits: {} sql: {}>'.format(
            self.traits, self.sqlBlock)


# Each of the 'expect' methods (corresponding to the states tabulated above)
# takes a token and returns a tuple (method, definition)
# where 'method' is the bound method to be invoked with the next token, and
# 'definition' is the definition that just finished parsing (or None if no
# definition was just finished).
#
class Parser(object):
    def __init__(self):
        self.currentDef = None

    def _newDef(self, text):
        new = Definition()
        new.traits.append(_parseTrait(text))

        old = self.currentDef
        self.currentDef = new
        return old

    def start(self):
        return self._expectDefinition

    def _expectDefinition(self, token):
        '''
State Name             Token  Next State  Note / Action
---------------------  -----  ----------  ------------------------------------
(1) Expect Definition  E      (1)         Useless whitespace outside any def
                       C      (2)         Add definition and first trait
                       I      Error       SQL must be preceded by an empty line
                       $      Success     This file was all whitespace or empty
        '''
        if token.kind == Kind.EMPTY_LINE:
            return self._expectDefinition, None
        elif token.kind == Kind.COMMAND_LINE:
            return self._expectCommand, self._newDef(token.text)
        else:
            enforce(token.kind == Kind.INDENTED_LINE, 'Bad: {}'.format(token))
            raise Exception('Unexpected indent at: "{}"'.format(token.text))

    def _expectCommand(self, token):
        '''
State Name             Token  Next State  Note / Action
---------------------  -----  ----------  ------------------------------------
(2) Expect Command     E      (3)         Done with def or is SQL next?
                       C      (2)         Add trait to current def
                       I      Error       SQL must be preceded by an empty line
                       $      Success     This last def had only one trait
        '''
        if token.kind == Kind.EMPTY_LINE:
            return self._expectDefinitionOrSql, None
        elif token.kind == Kind.COMMAND_LINE:
            self.currentDef.traits.append(_parseTrait(token.text))
            return self._expectCommand, None
        else:
            enforce(token.kind == Kind.INDENTED_LINE, 'Bad: {}'.format(token))
            raise Exception('Unexpected indent at: "{}"'.format(token.text))

    def _expectDefinitionOrSql(self, token):
        '''
State Name             Token  Next State  Note / Action
---------------------  -----  ----------  ------------------------------------
(3) Expect Def or SQL  E      (1)         Current definition is done
                       C      (2)         Add definition and first trait
                       I      (4)         Add SQL block to current def
                       $      Success     This last def had only one trait
        '''
        if token.kind == Kind.EMPTY_LINE:
            return self._expectDefinition, None
        elif token.kind == Kind.COMMAND_LINE:
            return self._expectCommand, self._newDef(token.text)
        else:
            enforce(token.kind == Kind.INDENTED_LINE, 'Bad: {}'.format(token))
            self.currentDef.sqlBlock = [token.text]
            return self._expectSql, None

    def _expectSql(self, token):
        '''
State Name             Token  Next State  Note / Action
---------------------  -----  ----------  ------------------------------------
(4) Expect sql or end  E      (1)         Current def had a one line SQL query
                       C      Error       Need empty line between SQL and def
                       I      (4)         Adding more lines to the current SQL
                       $      Success     The last def's SQL just ended
        '''
        if token.kind == Kind.EMPTY_LINE:
            return self._expectDefinition, None
        elif token.kind == Kind.COMMAND_LINE:
            raise Exception('Need an empty line between indented section and '
                            'unindented section at: {}'.format(token))
        else:
            enforce(token.kind == Kind.INDENTED_LINE, 'Bad: {}'.format(token))
            self.currentDef.sqlBlock.append(token.text)
            return self._expectSql, None


def parse(tokenGenerator):
    parser = Parser()
    f = parser.start()
    for token in tokenGenerator:
        f, newDefinition = f(token)
        if newDefinition:
            yield newDefinition

    # Leftovers
    if parser.currentDef:
        yield parser.currentDef


if __name__ == '__main__':
    import sys
    for definition in parse(lexer.lex(sys.stdin)):
        print(definition)
        print()
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

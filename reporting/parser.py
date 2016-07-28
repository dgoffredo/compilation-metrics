
from __future__ import print_function

'''
This parser has four states (excluding the end states "error" and "success"),
transitions among which are described below:

The following abbreviations are used for the token kinds:
    E = TokenKind.EMPTY_LINE
    C = TokenKind.COMMAND_LINE
    I = TokenKind.INDENTED_LINE
    $ = TokenKind.END

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

import lexer
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
    assert len(words) >= 3, template.format(text, words)
    return Trait(name=words[1], args=words[2:])                                                                         

class Definition(object):
    def __init__(self):
        self.traits = []
        self.sqlBlock = None

    def __str__(self):
        return '<definition traits: {} sql: {}>'.format(self.traits, self.sqlBlock)


# Each of the 'expect' methods (corresponding to the states tabulated above)
# takes a token and returns the bound method to be invoked with the next token,
# or returns None if parsing is complete. Each function raises an Exception on
# error.
#
class Parser(object):
    def __init__(self):
        self.definitions = []

    def _currentDef(self):
        assert len(self.definitions) > 0
        return self.definitions[-1]

    def _newDefinition(self, text):
        first = Definition()
        first.traits.append(_parseTrait(text))
        self.definitions.append(first)

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
            return self._expectDefinition
        elif token.kind == Kind.COMMAND_LINE:
            self._newDefinition(token.text)
            return self._expectCommand
        else: 
            assert token.kind == Kind.INDENTED_LINE, 'Bad: {}'.format(token)
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
            return self._expectDefinitionOrSql
        elif token.kind == Kind.COMMAND_LINE:
            self._currentDef().traits.append(_parseTrait(token.text))
            return self._expectCommand
        else: 
            assert token.kind == Kind.INDENTED_LINE, 'Bad: {}'.format(token)
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
            return self._expectDefinition
        elif token.kind == Kind.COMMAND_LINE:
            self._newDefinition(token.text)
            return self._expectCommand
        else: 
            assert token.kind == Kind.INDENTED_LINE, 'Bad: {}'.format(token)
            self._currentDef().sqlBlock = [token.text]
            return self._expectSql

    def _expectSql(self, token):
        '''
(4) Expect sql or end  E      (1)         Current def had a one line SQL query
                       C      Error       Need empty line between SQL and def
                       I      (4)         Adding more lines to the current SQL
                       $      Success     The last def's SQL just ended
        '''
        if token.kind == Kind.EMPTY_LINE:
            return self._expectDefinition
        elif token.kind == Kind.COMMAND_LINE:
            raise Exception('Need an empty line between indented section and '
                            'unindented section at: {}'.format(token))
        else: 
            assert token.kind == Kind.INDENTED_LINE, 'Bad: {}'.format(token)
            self._currentDef().sqlBlock.append(token.text)
            return self._expectSql

def parse(tokenGenerator):
    parser = Parser()
    f = parser.start()
    for token in tokenGenerator:
        f = f(token)

    return parser.definitions

if __name__ == '__main__':
    import sys
    for definition in parse(lexer.lex(sys.stdin)):
        print(definition)
        print()
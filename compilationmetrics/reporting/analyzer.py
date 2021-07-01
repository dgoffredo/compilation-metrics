from ..enforce import enforce
from . import iso8601

# TODO Document


class Plot(object):
    def __init__(self, imageName):
        self.imageName = imageName
        self.query = None  # Filled in later.
        self.width = 800
        self.height = 600
        self.xAxisLabel = None
        self.yAxisLabel = None
        self.yMin = None
        self.yMax = None
        self.style = 'horizontal-bars'
        self.system = None  # 'system' is for fixing Machine.System in SQL,
        # e.g. 'Linux', 'AIX', or 'SunOS' (from uname).
        self.period = None  # The interval of 'start' datetimes to consider.
        # If not specified, then it's the largest interval
        # in the database (i.e. no restriction).
        # If this attribute is not None, then it's a tuple
        # (begin, end).
        # TBD inclusive, exclusive?

    def __repr__(self):
        return str(self.__dict__)


def analyze(definitions):
    if isinstance(definitions, dict):
        # Treat it as json.
        for plot in analyzeJson(definitions):
            yield plot
    else:
        # Treat it as a generator.
        for plot in analyzeDefinitions(definitions):
            yield plot


def analyzeDefinitions(definitionGenerator):
    queries = dict()  # {name: sql}
    for definition in definitionGenerator:
        queries, plot = analyzeDefinition(definition, queries)
        if plot:
            yield plot


def defineQuery(definition):
    firstTrait = definition.traits[0]
    enforce(len(definition.traits) == 1, '"define-query" cannot have traits.')
    enforce(definition.sqlBlock is not None, '"define-query" must have SQL.')
    enforce(len(firstTrait.args) == 1, '"define-query" must have a name only.')
    queryName = firstTrait.args[0]
    sql = ''.join(definition.sqlBlock)
    return queryName, sql


def definePlot(definition, queries):
    firstTrait = definition.traits[0]
    enforce(firstTrait.name == 'define-plot',
            'Bad definition "{}"'.format(firstTrait.name))
    enforce(len(firstTrait.args) == 1, '"define-plot" must have a name only.')
    imageName = firstTrait.args[0]
    traits = definition.traits[1:]
    plot = Plot(imageName)

    if definition.sqlBlock is not None:
        plot.query = ''.join(definition.sqlBlock)

    def setQuery(trait):
        enforce(len(trait.args) == 1, 'A query reference needs (only) a name.')
        sqlDuped = definition.sqlBlock is not None
        enforce(not sqlDuped,
                'Both a "query" trait and a SQL block were specified.')
        queryName = trait.args[0]
        enforce(plot.query is None, 'query specified more than once.')
        query = queries.get(queryName)
        enforce(query, 'Unknown query for name "{}"'.format(queryName))
        plot.query = query

    def setStyle(trait):
        enforce(len(trait.args) == 1, 'A style needs (only) a name.')
        style = trait.args[0]
        whiteset = {'bars', 'line'}
        enforce(style in whiteset, 'Unknown style "{}"'.format(style))
        plot.style = style

    def setPeriod(trait):
        enforce(len(trait.args) == 2, 'A period needs two datetime arguments.')
        args = trait.args
        parse = iso8601.parse
        begin, end = parse(args[0]), parse(args[1])
        enforce(begin < end,
                'The datetime range must be positive and nonempty.')
        plot.period = begin, end

    def setAttribute(attribute, constructor):
        def setter(trait):
            enforce(
                len(trait.args) == 1,
                'A {} specifier needs only one argument.'.format(attribute))
            setattr(plot, attribute, constructor(trait.args[0]))

        return setter

    traitHandlers = {
        'query': setQuery,
        'width': setAttribute('width', int),
        'height': setAttribute('height', int),
        'system': setAttribute('system', str),
        'xAxisLabel': setAttribute('xAxisLabel', str),
        'yAxisLabel': setAttribute('yAxisLabel', str),
        'yMin': setAttribute('yMin', float),
        'yMax': setAttribute('yMax', float),
        'style': setStyle,
        'period': setPeriod
    }

    for trait in traits:
        name = trait.name
        handler = traitHandlers.get(name)
        enforce(handler is not None, 'Unknown trait "{}"'.format(name))
        handler(trait)

    return plot


def analyzeDefinition(definition, queries):
    enforce(len(definition.traits) != 0, 'Must have at least one trait.')
    firstTrait = definition.traits[0]
    enforce(len(firstTrait.args) != 0, '"define" trait must have an argument.')

    if firstTrait.name == 'define-query':
        queryName, sql = defineQuery(definition)
        enforce(queryName not in queries,
                'Duplicate query name "{}"'.format(queryName))
        queries[queryName] = sql
        return queries, None  # No plot
    else:
        plot = definePlot(definition, queries)
        return queries, plot


def analyzeJson(defs):
    raise Exception('Not yet implemented.')  # TODO


if __name__ == '__main__':
    import sys
    from .lexer import lex
    from .parser import parse

    for plot in analyze(parse(lex(sys.stdin))):
        for key, value in plot.__dict__.items():
            print('    ', key, '-->', value)
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

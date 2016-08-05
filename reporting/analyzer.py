
from __future__ import print_function

import iso8601

# TODO Document

class Plot(object):
    def __init__(self, imageName):
        self.imageName = imageName
        self.query = None # Filled in later.
        self.queryRef = None # Might or might not exist.
        self.width = 2 * 1024
        self.height = 2 * 768
        self.xAxisLabel = None
        self.yAxisLabel = None
        self.style = 'bars'
        self.system = None # 'system' is for fixing Machine.System in SQL,
                           # e.g. 'Linux', 'AIX', or 'SunOS' (from uname).
        self.period = None # The interval of 'start' datetimes to consider.
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
        return analyzeJson(definitions)
    else:
        # Treat it as a generator.
        return analyzeDefinitions(definitions)

def analyzeDefinitions(definitionGenerator):
    queries = dict() # {name: sql}
    plots = dict() # {name: Plot}
    for definition in definitionGenerator:
        queries, plots = analyzeDefinition(definition, queries, plots)

    # Lookup the referred-to queries (if there are any).
    for plot in plots.itervalues():
        queryName = plot.queryRef
        if queryName is None:
            assert plot.query is not None, 'Plot must have query or query reference.'
            continue
        sql = queries.get(queryName)
        assert sql is not None, 'Undefined SQL query "{}"'.format(queryName)
        plot.query = sql

    return plots

def defineQuery(definition):
    firstTrait = definition.traits[0]
    assert len(definition.traits) == 1, '"define-query" cannot have traits.' 
    assert definition.sqlBlock is not None, '"define-query" must have SQL.'
    assert len(firstTrait.args) == 1, '"define-query" must have a name only.'
    queryName = firstTrait.args[0]
    sql = ''.join(definition.sqlBlock)
    return queryName, sql

def definePlot(definition):
    firstTrait = definition.traits[0]
    assert firstTrait.name == 'define-plot', 'Bad definition "{}"'.format(firstTrait.name)
    assert len(firstTrait.args) == 1, '"define-plot" must have a name only.'
    imageName = firstTrait.args[0]
    traits = definition.traits[1:]
    plot = Plot(imageName)

    if definition.sqlBlock is not None:
        plot.query = ''.join(definition.sqlBlock)

    def setQuery(trait):
        assert len(trait.args) == 1, 'A query reference needs (only) a name.'
        sqlDuped = definition.sqlBlock is not None
        assert not sqlDuped, 'Both a "query" trait and a SQL block were specified.'
        queryName = trait.args[0]
        assert plot.queryRef is None, 'query specified more than once.'
        plot.queryRef = queryName

    def setStyle(trait):
        assert len(trait.args) == 1, 'A style needs (only) a name.'
        style = trait.args[0]
        whiteset = {'bars', 'line'}
        assert style in whiteset, 'Unknown style "{}"'.format(style)
        plot.style = style

    def setPeriod(trait):
        assert len(trait.args) == 2, 'A period needs two datetime arguments.'
        args = trait.args
        parse = iso8601.parse
        begin, end = parse(args[0]), parse(args[1])
        assert begin < end, 'The datetime range must be positive and nonempty.'
        plot.period = begin, end

    def setAttribute(attribute, constructor):
        def setter(trait):
            assert len(trait.args) == 1, 'A {} specifier needs only one argument.'.format(attribute)
            setattr(plot, attribute, constructor(trait.args[0]))
        return setter

    traitHandlers = {
        'query': setQuery,
        'width': setAttribute('width', int),
        'height': setAttribute('height', int),
        'system': setAttribute('system', str),
        'xAxisLabel': setAttribute('xAxisLabel', str),
        'yAxisLabel': setAttribute('yAxisLabel', str),
        'style': setStyle,
        'period': setPeriod
    }

    for trait in traits:
        name = trait.name
        handler = traitHandlers.get(name)
        assert handler is not None, 'Unknown trait "{}"'.format(name)
        handler(trait)

    return plot

def analyzeDefinition(definition, queries, plots):
    assert len(definition.traits) != 0, 'Must have at least one trait.'
    firstTrait = definition.traits[0]
    assert len(firstTrait.args) != 0, '"define" trait must have an argument.'

    if firstTrait.name == 'define-query':
        queryName, sql = defineQuery(definition)
        assert queryName not in queries, 'Duplicate query name "{}"'.format(queryName)
        queries[queryName] = sql
    else:
        plot = definePlot(definition)
        plots[plot.imageName] = plot

    return queries, plots

def analyzeJson(defs):
    raise Exception('Not yet implemented.') # TODO

if __name__ == '__main__':
    import sys
    from lexer import lex
    from parser import parse

    plots = analyze(parse(lex(sys.stdin)))
    for name, plot in plots.iteritems():
        print(name)
        for key, value in plot.__dict__.iteritems():
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

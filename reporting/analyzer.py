
from __future__ import print_function

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

    def __repr__(self):
        return str(self.__dict__)

def analyze(definitions):
    if isinstance(definitions, dict):
        return analyzeJson(definitions)
    else:
        assert isinstance(definitions, list), 'Argument be a dict or a list.'
        return analyzeDefinitions(definitions)

def analyzeDefinitions(definitions):
    queries = dict() # {name: sql}
    plots = dict() # {name: Plot}
    for definition in definitions:
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
        'style': setStyle
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

    definitions = list(parse(lex(sys.stdin)))
    for name, plot in analyze(definitions).iteritems():
        print(name)
        for key, value in plot.__dict__.iteritems():
            print('    ', key, '-->', value)    
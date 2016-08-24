
'''

Lines are read from input and passed through the data pipeline shown below.

The stream of lines is passed through a lexer and parser and then analyzed 
to yield a stream of plot descriptors, which are then passed along with a
database path into a query engine whose result records are then streamed
into an output file (per plot), a gnuplot-generated image (per-plot), and
an "appendix" HTML file.

                                                             +--> [data file]
                                                             |
[input] --> [lex] --> [parse] --> [analyze] --+              +--> [gnuplot]
                                              |              |
                                              +--> [query] --+
                                              |              |
[database] ----------------->-----------------+              +--> [appendix]

'''

import gnuplot
import appendix
import plotter
import markdown
import lexer
import parser
import analyzer
from ..database.read import query

import os

def _mkdir(folderPath):
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

def _analyzePlotsFile(plotsFile):
    lex = lexer.lex
    parse = parser.parse
    analyze = analyzer.analyze

    return analyze(parse(lex(plotsFile)))

# plotsFile: File object from which to read plot/query descriptions.
# reportMarkdownFile: File object containing the report in markdown notation.
# rootFolder: Path to the output directory.
#
def generate(plotsFile, reportMarkdownFile, rootFolder, databaseName=None):

    _mkdir(rootFolder)
    with open(os.path.join(rootFolder, 'index.html'), 'w') as indexHtmlFile:
        markdown.toHtml(reportMarkdownFile, indexHtmlFile)
    
    imageFolder = os.path.join(rootFolder, 'images')
    _mkdir(imageFolder)

    appendix.installDependencies(rootFolder)

    with gnuplot.Gnuplot() as gp, \
         appendix.Builder(rootFolder, imageFolder) as appendixBuilder:
        for plot in _analyzePlotsFile(plotsFile):
            appendixBuilder.beginPlot(plot)
            with plotter.Renderer(plot, imageFolder, gp) as renderer:
                for dataRecord in query(plot, databaseName):
                    renderer.addRecord(dataRecord)
                    appendixBuilder.addRecord(dataRecord)

if __name__ == '__main__':
    import sys
    plotsFile = sys.stdin
    rootFolder = '.'
    with open(sys.argv[1]) as reportMarkdownFile:
        generate(plotsFile, reportMarkdownFile, rootFolder)
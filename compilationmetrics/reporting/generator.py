
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

from . import gnuplot
from . import appendix
from . import plotter
from . import markdown
from . import lexer
from . import parser
from . import analyzer
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
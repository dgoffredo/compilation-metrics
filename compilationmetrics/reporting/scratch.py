
# New modules:
#    database: Runs the queries
#    plotter:  Renders the plots
#    appendix: Generates the detail html page (not the markdown report)

# New classes and generators:
#    appendix.Builder: streams to HTML
#    analyzePlotsFile: spits out named plot descriptors
#    plotter.Renderer: streams points to a gnuplot process that writes png,
#                      and will rotate the image afterwards if necessary.
#    database.query:   connects to database, creates view(s), and spits out
#                      query results as they come in.        

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

with gnuplot.Gnuplot() as gp, \
     appendix.Builder(rootFolder, imageFolder) as appendixBuilder:
    for plot in analyzePlotsFile(plotsFile):
        appendixBuilder.beginPlot(plot)
        with plotter.Renderer(plot, imageFolder, gp) as renderer:
            for dataRecord in database.query(plot):
                renderer.addRecord(dataRecord)
                appendixBuilder.addRecord(dataRecord)

'''
In a C++ like language, that would be this:

let gp = Gnuplot()
let appendixBuilder = appendix.Builder(rootFolder, imageFolder)

for plot in analyzePlotsFile(plotsFile):
    appendixBuilder.beginPlot(plot)
    let renderer = plotter.Renderer(plot, imageFolder, gp)
    for dataRecord in database.query(plot):
        renderer.addRecord(dataRecord)
        appendixBuilder.addRecord(dataRecord)

'''

# Pieces to be built:
#     - gnuplot scripts (including rotate)
#     - appendix html outputter

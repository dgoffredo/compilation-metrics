

'''
with gnuplot.Gnuplot() as gp, \
     appendix.Builder(rootFolder, imageFolder) as appendixBuilder:
    for plot in analyzePlotsFile(plotsFile):
        appendixBuilder.beginPlot(plot)
        with plotter.Renderer(plot, imageFolder, gp) as renderer:
            for dataRecord in database.query(plot):
                renderer.writeDataRow(dataRecord)
                appendixBuilder.writeDataRow(dataRecord)
'''

from contextlib import contextmanager
import gnuplot

def _finishPlot(gnuplotInstance):
    gp = gnuplotInstance
    if gp.isPlottingData:
        gp.endDataSection()

_styleTemplates = {
    'horizontal-bars': '''
unset key

set style data histogram
set style histogram cluster gap 1
set style fill solid border -1

set boxwidth 0.25

set xtics nomirror rotate by 90 right
set x2label '{xlabel}'
unset x2tics

set ytics nomirror rotate by 90
set ylabel '{ylabel}'
set yrange [{yMin}:{yMax}]

plot '-' using 2:xticlabel(1)
'''
} # TODO: Who does the yMax==None --> '*' thing? 

def _setupPlot(plot, imageFolder, gnuplotInstance):
    gp = gnuplotInstance
    # TODO

@contextmanager
def Renderer(plot, imageFolder, gnuplotInstance=None):
    localGp, gp = None, None
    if gnuPlotInstance is None:
        gp = localGp = gnuplot.Gnuplot()
    else:
        gp = gnuplotInstance

    _setupPlot(plot, imageFolder, gp)
    yield gp
    _finishPlot(gp)

    if localGp is not None:
        localGp.quit()
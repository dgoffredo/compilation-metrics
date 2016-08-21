

from __future__ import print_function
from contextlib import contextmanager
import gnuplot
import json
import os.path
import tempfile

def _doubleQuote(s):
    s = s if isinstance(s, basestring) else str(s)
    return json.dumps(s)

from select import PIPE_BUF

def _rotate(plot, imageFolder, gp):
    imagePath = os.path.join(imageFolder, plot.imageName)

    bufferFiller = ''.join('x' for _ in range(2 * PIPE_BUF)) 

    template = '\n'.join([
        "reset",
        "",
        "set size ratio -1",
        "set lmargin 0",
        "set rmargin 0",
        "set tmargin 0",
        "set bmargin 0",
        "unset tics",
        "unset border",
        "",
        # Do a no-op plot to collect the size info of the input image.
        "plot {inFile} binary filetype=png rotate=-90deg w rgbima notitle",
        "",
        "xmax=GPVAL_DATA_X_MAX",
        "xmin=GPVAL_DATA_X_MIN",
        "ymin=GPVAL_DATA_Y_MIN",
        "ymax=GPVAL_DATA_Y_MAX",
        "",
        "set xrange [xmin:xmax]",
        "set yrange [ymin:ymax]",
        "set term png truecolor size (xmax-xmin),(ymax-ymin)",
        "",
        "set output {outFile}",
        "plot {inFile} binary filetype=png rotate=-90deg w rgbima notitle"
    ]) + '\n'

    tempFolder = tempfile.mkdtemp()
    tempPath = os.path.join(tempFolder, 'tmp.png')
    print('Going to try to rotate', imagePath,
          'using the temporary file', tempPath)

    script = template.format(inFile=_doubleQuote(imagePath),
                             outFile=_doubleQuote(tempPath),
                             filler=_doubleQuote(bufferFiller))

    print('Rotation script:\n\n{}'.format(script))
    print('Rotating...')
    gp.send(script)

    gp.closeOutput()
    
    # TODO: It'd be better to do this using shutil, but then there's a race
    #       between this and gnuplot finishing its plotting. I tried
    #       to synchronize them using gnuplot's stderr via the 'print'
    #       command, but I couldn't get the buffering right.
    #       The bummer is that this will fork twice for each rotation :( 
    #
    gp.send('!mv {} {}'.format(_doubleQuote(tempPath), _doubleQuote(imagePath)))
    gp.send('!rm -r {}'.format(_doubleQuote(tempFolder)))

def _horizontalBars(xAxisLabel, yAxisLabel, yMin, yMax):
    template  = '\n'.join([
        "unset key",

        "set style data histogram",
        "set style histogram cluster gap 1",
        "set style fill solid border -1",

        "set boxwidth 0.25",

        "set xtics nomirror rotate by 90 right",
        "set x2label {xlabel}",
        "unset x2tics",

        "set ytics nomirror rotate by 90",
        "set ylabel {ylabel}",
        "set yrange [{yMinOrStar}:{yMaxOrStar}]",

        "plot '-' using 2:xticlabel(1)"
    ]) + '\n'

    def ifNone(value, valueIfNone):
        return valueIfNone if value is None else value

    return template.format(xlabel=_doubleQuote(ifNone(xAxisLabel, ' ')), 
                           ylabel=_doubleQuote(ifNone(yAxisLabel, ' ')),
                           yMinOrStar=ifNone(yMin, '*'),
                           yMaxOrStar=ifNone(yMax, '*'))

_styles = {
    'horizontal-bars': _horizontalBars
}

_rotatedStyles = frozenset(['horizontal-bars'])

# Every plot is a png with a (file)name, a width, and a height.
# This function returns gnuplot commands that clear any previous configuration
# and prepare the output for 'plot'.
def _boilerplate(plot, imageFolder):
    assert plot.imageName is not None, 'A plot must have an image name.'
    imagePath = os.path.join(imageFolder, plot.imageName)

    # If the 'style' of this plot involves a rotation of the entire image,
    # then when first drawing the plot, swap 'width' and 'height' so that the
    # specified 'width' and 'height' end up referring to the dimensions of the
    # rotated image. Assume that all rotations are plus or minus 90 degrees.
    if plot.style in _rotatedStyles:
        width, height = plot.height, plot.width
    else:
        width, height = plot.width, plot.height

    template = '\n'.join([
        "reset",
        "set terminal png size {width}, {height} nocrop",
        "set output {name}"
    ]) + '\n'

    return template.format(width=width, 
                           height=height, 
                           name=_doubleQuote(imagePath))

def _setupPlot(plot, imageFolder, gnuplotInstance):
    gp = gnuplotInstance

    style = plot.style
    assert style in _styles, 'Unknown style "{}"'.format(style)

    # Send the boilerplate commands (reset, set terminal, etc.).
    gp.send(_boilerplate(plot, imageFolder))

    # Send the plot command. Afterwards, gnuplot will be waiting for plot data.
    gp.send(_styles[style](plot.xAxisLabel, 
                           plot.yAxisLabel, 
                           plot.yMin, 
                           plot.yMax))

def _finishPlot(plot, imageFolder, gp):
    gp.endDataSection()
    gp.closeOutput()
    if plot.style in _rotatedStyles:
        _rotate(plot, imageFolder, gp)

# If the argument is None, then yield a scoped Gnuplot instance.
# If the argument is not None, then yield the argument without any additional
# scoping.
@contextmanager
def scopeOrNope(gp):
    if gp is None:
        with gnuplot.Gnuplot() as scopedGp:
            yield scopedGp
    else:
        yield gp

# RendererHandle is a restriction on gnuplot.Gnuplot. It allows a holder to
# write plot data (i.e. data points) to a Gnuplot, but that's it.
class RendererHandle(object):
    def __init__(self, gnuplotInstance):
        self._gp = gnuplotInstance

    # 'row' is an iterable.
    def writeDataRow(self, row):
        return self._gp.writeDataRow(row)

@contextmanager
def Renderer(plot, imageFolder, gnuplotInstance=None):
    with scopeOrNope(gnuplotInstance) as gp:
        _setupPlot(plot, imageFolder, gp)
        yield RendererHandle(gp)
        _finishPlot(plot, imageFolder, gp)

if __name__ == '__main__':
    import analyzer
    import math
    import sys
    import signal

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    plot = analyzer.Plot('foo.png')
    plot.yAxisLabel = 'sin(x)'
    plot.xAxisLabel = 'x (radians)' 

    if len(sys.argv) == 3:
        plot.width = int(sys.argv[1])
        plot.height = int(sys.argv[2])

    imageFolder = './'

    def coeff(nPoints):
        return math.pi / float(nPoints)

    with Renderer(plot, imageFolder) as renderer:
        # Plot n values of sin(x) for x between 0 and pi.
        n = 50
        for x in (i * coeff(n) for i in range(n)):
            renderer.writeDataRow(['sin({:.2f})'.format(x), math.sin(x)])
            
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
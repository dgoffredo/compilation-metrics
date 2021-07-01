# Takes Plot objects and data records and produces HTML output containing
# the name, image, and configuration of each Plot along with a table of its
# data values.
# See 'Builder'.

from ..enforce import enforce

from contextlib import contextmanager
import os.path
import html
import shutil
import datetime


def _isDatetime(value):
    return isinstance(value, datetime.datetime)


def _isDatetimeRange(value):
    try:
        begin, end = value
        return _isDatetime(begin) and _isDatetime(end)
    except:
        return False


def _datetimeRangeToString(value):
    begin, end = value
    return '{} to {}'.format(begin.isoformat(), end.isoformat())


def _escape(s):
    if _isDatetimeRange(s):
        s = _datetimeRangeToString(s)
    elif not isinstance(s, str):
        s = str(s)

    # html.escape does angle brackets, ampersands, double quotes, and single quotes.
    return html.escape(s, quote=True)


def _addRecord(row, write):
    write('<tr>\n')
    for data in row:
        write('<td>{}</td>'.format(_escape(data)))
    write('</tr>\n')


def _finishPlot(write, last=False):
    write('</table>\n</p>\n\n')
    if not last:
        write('<hr />')


def _ifNone(value, default):
    return default if value is None else value


def _beginHtml(write):
    write('''<!DOCTYPE html>
<html>
<head>
<style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
}

td, th {
    border: 1px solid #eeeeee;
    text-align: left;
    padding: 8px;
}

tr:nth-child(even) {
    background-color: #dddddd;
}
</style>

<link rel="stylesheet" 
      href="highlight/styles/default.css">
<script src="highlight/highlight.pack.js"></script>
<script>hljs.initHighlightingOnLoad();</script>

</head>
<body>
 ''')


def _finishHtml(write):
    write('</body>\n</html>\n')


def _beginPlot(plot, imageFolder, write):
    # Header with imageName
    imageName = _escape(plot.imageName)
    write('<h1 id="{0}">{0}</h1>\n\n'.format(imageName))

    # The image
    imagePath = _escape(os.path.join(imageFolder, plot.imageName))
    write('<img src="{}" />\n\n'.format(imagePath))

    # Attributes table
    write('<h2>Attributes</h2>\n')
    write('<p>\n')
    write('<table>\n')
    write('<tr><th>Attribute</th><th>Value</th></tr>\n')
    for attr, value in plot.__dict__.items():
        if attr == 'query':
            continue  # The query is printed elsewhere
        write('<tr><td>{}</td><td>{}</td></tr>\n'.format(
            _escape(attr), _escape(_ifNone(value, ''))))
    write('</table></p>\n\n')

    # Query
    write('<h2>Query</h2>\n')
    write('<p>\n')
    write('<pre><code class="sql">')
    write(_escape(plot.query))
    write('</code></pre></p>\n\n')

    # Data table (partial)
    write('<h2>Data</h2>\n')
    write('<p>\n')
    write('<table>\n')
    write('<tr><th>{xTitle}</th><th>{yTitle}</th></tr>\n'.format(
        xTitle=_escape(_ifNone(plot.xAxisLabel, 'X Value')),
        yTitle=_escape(_ifNone(plot.yAxisLabel, 'Y Value'))))


def _scriptDir():
    return os.path.dirname(os.path.realpath(__file__))


def installDependencies(rootFolder):
    folder = os.path.join(_scriptDir(), 'highlight')
    enforce(os.path.exists(folder), 'Expected {} to exists.'.format(folder))

    destination = os.path.join(rootFolder, 'highlight')
    if os.path.exists(destination):
        shutil.rmtree(destination, ignore_errors=True)
    shutil.copytree(folder, destination)


# An object that exposes two functions. The functions must be passed in as
# constructor arguments.
class BuilderHandle(object):
    def __init__(self, beginPlot, addRecord):
        self.beginPlot = beginPlot
        self.addRecord = addRecord


class _Flag(object):
    def __init__(self, initial=False):
        self.value = initial

    def __nonzero__(self):
        return self.value

    def set(self, value):
        self.value = value


@contextmanager
def Builder(rootFolder, imageFolder, fileName='appendix.html'):
    # 'imageFolder' must be expressed relative to 'rootFolder'.
    with open(os.path.join(rootFolder, fileName), 'w') as out:
        _beginHtml(out.write)
        hasPlots = _Flag()

        def beginPlot(plot):
            if hasPlots:
                # Close the previous entry.
                _finishPlot(out.write)
            else:
                hasPlots.set(True)
            _beginPlot(plot, imageFolder, out.write)

        def addRecord(row):
            _addRecord(row, out.write)

        # Let the caller begin plots and add records to those plots.
        yield BuilderHandle(beginPlot, addRecord)

        if hasPlots:
            _finishPlot(out.write, last=True)

        _finishHtml(out.write)


if __name__ == '__main__':
    import analyzer

    plot = analyzer.Plot('foo.png')
    plot.yAxisLabel = 'sin(x)'
    plot.xAxisLabel = 'x (radians)'
    plot.query = 'select Thing, count(*) as HowMany\n' \
                 'from Table\n' \
                 'where Whatever > 343\n' \
                 'order by HowMany desc;'
    root = '../../examples'
    images = 'images'

    with Builder(root, images) as builder:
        builder.beginPlot(plot)
        builder.addRecord([2.2, 2322.112])
        builder.addRecord([2.3, 33221])
        builder.addRecord([5.6, 45544.23])
        builder.addRecord(['Infinity', 0])
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

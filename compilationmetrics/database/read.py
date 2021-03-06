# Provides a generator 'query' that manages a connection with a sqlite3
# database file and runs its SQL query argument in an environment having
# a view (virtual read-only table) for convenience.

from .open import connect
from contextlib import contextmanager


def _createVariablesTempTable(db, name, variables):
    columns = ', '.join(variables.keys())
    db.execute('create temporary table {name}({columns});'.format(
        name=name, columns=columns))

    values = ', '.join(':{}'.format(column) for column in variables.keys())
    db.execute(
        'insert into {name}({columns}) values({values});'.format(
            name=name, columns=columns, values=values), variables)

    db.commit()


def _makeWhereClause(db, tempTableName, plot):
    predicates = []
    variables = {'begin': None, 'end': None, 'system': None}

    def setAndSelectVariable(name, value):
        variables[name] = value
        return '(select {name} from {table})'.format(name=name,
                                                     table=tempTableName)

    if plot.period:
        begin, end = plot.period
        predicates.append('Compilation.StartIso8601 between {} and {}'.format(
            setAndSelectVariable('begin', begin),
            setAndSelectVariable('end', end)))

    if plot.system:
        predicates.append('Machine.System = {}'.format(
            setAndSelectVariable('system', plot.system)))

    if len(predicates) == 0:
        whereClause = ''
    else:
        whereClause = 'where ' + ' and '.join(predicates)
        _createVariablesTempTable(db, tempTableName, variables)

    return whereClause


_viewDescriptionTemplate = '''
create temporary view {viewName} as
select 
       /* All fields from the main table (Compilation) */
       Compilation.*

       /* Computed convenience columns */
     , UserCpuTime + SystemCpuTime                        as CpuTime
     , BlockingInputOperations + BlockingOutputOperations as BlockingOperations

       /* Some fields from the joined-in tables */
     , File.Name                                          as FileName
     , File.Path                                          as FilePath
     , File.LineCount                                     as FileLineCount
     , File.PreprocessedSizeBytes                         as FilePreprocessedSizeBytes
     , File.PreprocessedLineCount                         as FilePreprocessedLineCount
     , Machine.Name                                       as MachineName
     , Machine.System                                     as MachineSystem

       /* Aliases for other columns */
     , Machine.System                                     as System
     , Compilation.StartIso8601                           as Start
     , Compilation.DurationSeconds                        as Duration
     , Compilation.MaxResidentMemoryBytes                 as Memory
from Compilation 
inner join Machine on Compilation.MachineKey = Machine.Key
inner join File    on Compilation.FileKey = File.Key
{whereClause};
'''


@contextmanager
def _scopedView(db, plot):
    # Build the query that will define the SQL view.
    # In building the 'where' clause that will be used in the definition of
    # the view, a temporary table might have to be added to the database.
    # This is because sqlite does not allow for parameters in CREATE VIEW
    # statements. In order to parameterize the restrictions on begin time,
    # end time, system, etc. a temporary table has to be created, so that
    # the select using in the view definition can refer to parameters bytearray
    # selecting from the temporary table.
    # If 'plot' has no restrictions, then no temporary table will be created.
    #
    tempTableName = 'CompilationViewParameters'
    whereClause = _makeWhereClause(db, tempTableName, plot)
    viewName = 'CompilationView'
    viewDesc = _viewDescriptionTemplate.format(viewName=viewName,
                                               whereClause=whereClause)

    # Create the view and expose the modified database connection to the
    # caller (who will be using this function in a 'with' statement).
    db.execute(viewDesc)
    db.commit()
    yield db

    # Now the caller is done with this view.
    db.execute('drop view {};'.format(viewName))
    db.execute('drop table if exists {};'.format(tempTableName))
    db.commit()


@contextmanager
def _databaseWithView(plot, databaseName):
    db = connect(databaseName)

    # Add a temporary view to our connection and expose it to the caller.
    with _scopedView(db, plot) as dbWithView:
        yield dbWithView

    # Now the caller is done with the connection.
    db.close()


def query(plot, databaseName=None):
    with _databaseWithView(plot, databaseName) as db:
        for row in db.execute(plot.query):
            yield row


if __name__ == '__main__':
    plotDesc = '''
.define-query 'longest-duration'

    select FileName, avg(DurationSeconds) as AverageDuration
    from CompilationView
    group by FileName
    order by AverageDuration desc
    limit 25;

.define-plot 'longest-duration-linux.png'
.query 'longest-duration'
.system 'Linux'
'''
    from ..reporting.lexer import lex
    from ..reporting.parser import parse
    from ..reporting.analyzer import analyze

    keepends = True
    for plot in analyze(parse(lex(plotDesc.splitlines(keepends)))):
        print('Going to run query for plot:\n', plot)
        print()
        for row in query(plot):
            print(row)
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

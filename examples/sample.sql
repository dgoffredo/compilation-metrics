.define-plot 'preprocessed-size.png'
.width 800
.height 600
.xAxisLabel 'Name of File Preprocessed'
.yAxisLabel 'Source Size After Preprocessor (Mebibytes)'

    select FileName, FilePreprocessedSizeBytes / 1024.0 / 1024.0 as SizeMib
    from CompilationView
    group by FileName
    order by FilePreprocessedSizeBytes desc
    limit 25;

.define-plot 'duration-linux.png'
.width 800
.height 600
.xAxisLabel 'Name of File Compiled'
.yAxisLabel 'Average Duration (seconds)'

    select FileName, avg(DurationSeconds) as AvgDuration
    from CompilationView
    where System = 'Linux'
    group by FileName
    order by AvgDuration desc
    limit 25;

.define-plot 'duration-per-line-linux.png'
.width 800
.height 600
.xAxisLabel 'Name of File Compiled'
.yAxisLabel 'Average Duration Per Line (milliseconds)'

    select FileName, avg(DurationSeconds / FileLineCount) * 1000 as AvgDurationPerLine
    from CompilationView
    where System = 'Linux'
    group by FileName
    order by AvgDurationPerLine desc
    limit 25;

.define-query 'memory'

    select FileName, 
           avg(MaxResidentMemoryBytes) / 1024 / 1024 as AvgMemMibis
    from CompilationView
    group by FileName
    order by AvgMemMibis desc
    limit 25;

.define-plot 'memory-linux.png'
.width 800
.height 600
.query 'memory'
.system 'Linux'
.xAxisLabel 'File Compiled'
.yAxisLabel 'Average Memory Consumed (mibibytes)'

.define-plot 'most-active-users.png'
.width 800
.height 600
.xAxisLabel 'User Name (Unix name)'
.yAxisLabel 'Number of Compilations'

    select User, count(*) as NumCompilations
    from CompilationView
    group by User
    order by NumCompilations desc
    limit 10;

.define-plot 'most-time-consuming-files.png'
.width 800
.height 600
.xAxisLabel 'Name of File Compiled'
.yAxisLabel 'Total Duration (seconds)'

    select FileName, sum(DurationSeconds) as TotalSeconds
    from CompilationView
    group by FileName
    order by TotalSeconds desc
    limit 10;

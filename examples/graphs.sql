
.plot 'duration-solaris.png'

    select f.Name, avg(c.DurationSeconds) as AvgDuration
    from CompilationView c inner join
         File f on c.FileKey = f.Key
    inner join Machine m on c.MachineKey = m.Key
    where m.System = 'SunOS'
    group by f.Name
    order by AvgDuration desc
    limit 25;

.plot 'duration-aix.png'

    select f.Name, avg(c.DurationSeconds) as AvgDuration
    from CompilationView c inner join
         File f on c.FileKey = f.Key
    inner join Machine m on c.MachineKey = m.Key
    where m.System = 'AIX'
    group by f.Name
    order by AvgDuration desc
    limit 25;

.define-plot 'duration-linux.png'
.width 1024
.height 768

    select f.Name, avg(c.DurationSeconds) as AvgDuration
    from CompilationView c inner join
         File f on c.FileKey = f.Key
    inner join Machine m on c.MachineKey = m.Key
    where m.System = 'Linux'
    group by f.Name
    order by AvgDuration desc
    limit 25;

.define-query 'memory'

    select f.Name, 
           avg(c.MaxResidentMemoryBytes) as AvgMem, 
           max(c.MaxResidentMemoryBytes) as MaxMem
    from CompilationView c inner join File f
       on c.FileKey = f.Key
    group by f.Name
    order by AvgMem desc
    limit 25;

.define-plot 'memory-solaris.png'
.query 'memory'
.system 'SunOS'

.define-plot 'memory-aix.png'
.query 'memory'
.system 'AIX'

.define-plot 'memory-linux.png'
.query 'memory'
.system 'Linux'

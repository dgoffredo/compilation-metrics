
.graph 'duration-solaris.png';

    select f.Name, avg(c.DurationSeconds) as AvgDuration
    from CompilationView c inner join
         File f on c.FileKey = f.Key
    inner join Machine m on c.MachineKey = m.Key
    where m.System = 'SunOS'
    group by f.Name
    order by AvgDuration desc
    limit 25;

.graph 'duration-aix.png';

    select f.Name, avg(c.DurationSeconds) as AvgDuration
    from CompilationView c inner join
         File f on c.FileKey = f.Key
    inner join Machine m on c.MachineKey = m.Key
    where m.System = 'AIX'
    group by f.Name
    order by AvgDuration desc
    limit 25;

.graph "duration-linux.png";

    select f.Name, avg(c.DurationSeconds) as AvgDuration
    from CompilationView c inner join
         File f on c.FileKey = f.Key
    inner join Machine m on c.MachineKey = m.Key
    where m.System = 'Linux'
    group by f.Name
    order by AvgDuration desc
    limit 25;

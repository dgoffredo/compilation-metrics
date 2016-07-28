
# <a name="duration-solaris.png">duration-solaris.png</a>

## Options
* ylabel: Seconds To Compile (Solaris)
* xlabel: Source File
* style: bar
* orientation: horizontal

## Query

    select f.Name, avg(c.DurationSeconds) as AvgDuration
    from CompilationView c inner join
         File f on c.FileKey = f.Key
    inner join Machine m on c.MachineKey = m.Key
    where m.System = 'SunOS'
    group by f.Name
    order by AvgDuration desc
    limit 25;

# <a name="duration-aix.png">duration-aix.png</a>

## Options
* ylabel: Seconds To Compile (AIX)
* xlabel: Source File
* style: bar
* orientation: horizontal

## Query

    select f.Name, avg(c.DurationSeconds) as AvgDuration
    from CompilationView c inner join
         File f on c.FileKey = f.Key
    inner join Machine m on c.MachineKey = m.Key
    where m.System = 'AIX'
    group by f.Name
    order by AvgDuration desc
    limit 25;

# duration-linux.png

## Options
* ylabel: Seconds To Compile (Linux)
* xlabel: Source File
* style: bar
* orientation: horizontal

## Query

    select f.Name, avg(c.DurationSeconds) as AvgDuration
    from CompilationView c inner join
         File f on c.FileKey = f.Key
    inner join Machine m on c.MachineKey = m.Key
    where m.System = 'Linux'
    group by f.Name
    order by AvgDuration desc
    limit 25;

# minimal.png

    select f.Name, avg(c.DurationSeconds) as AvgDuration
    from CompilationView c inner join
         File f on c.FileKey = f.Key
    inner join Machine m on c.MachineKey = m.Key
    where m.System = 'Linux'
    group by f.Name
    order by AvgDuration desc
    limit 25;

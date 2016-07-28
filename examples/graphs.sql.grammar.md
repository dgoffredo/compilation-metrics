# Plot/Query Description Grammar
A file describing a set of plots and their SQL queries must satisfy "*file*"
as defined in the grammar below. Note that the regular expressions need only
match the beginning of a line.

---------------------

*file &nbsp;::= &nbsp;empty-line&ast; &nbsp;spec? &nbsp;empty-line&ast;*

*spec &nbsp;::= &nbsp;definition &nbsp;(empty-line+ &nbsp;definition)&ast;*

*definition &nbsp;::= &nbsp;command+ &nbsp;(empty-line &nbsp;sql-block)?*

*sql-block &nbsp;::= &nbsp;indented+*

*empty-line &nbsp;::=&nbsp;* `/^\s*$/`

*command &nbsp;::=&nbsp;* `/^\.\s*\S/`

*indented &nbsp;::=&nbsp;* `/^[ ]{4}\s*\S/`

-----------------------------------

# Example
The grammar above doesn't assign any meaning to the "`command`s" or
"`sql-block`s," but this example illustrates possible usage:

    .define-plot 'duration-solaris.png'
    
        select f.Name, avg(c.DurationSeconds) as AvgDuration
        from CompilationView c inner join
             File f on c.FileKey = f.Key
        inner join Machine m on c.MachineKey = m.Key
        where m.System = 'SunOS'
        group by f.Name
        order by AvgDuration desc
        limit 25;
    
    .define-plot 'duration-aix.png'
    
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

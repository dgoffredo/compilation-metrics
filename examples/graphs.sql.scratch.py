# Sketch of part of a parser:

def iterbytes(file):
	ch = file.read(1)
	while ch != '':
		yield ch
		ch = file.read(1)

def statements(charIterator):
	chars = []
	inString = False
	for ch in charIterator:
		chars.append(ch)
		if ch == "'":
			inString = not inString
		elif ch == ';' and not inString:
			yield ''.join(chars).strip()
			del chars[:]
			
	# Remaining characters not terminated by a ';'
	if len(chars) != 0:
		yield ''.join(chars).strip()
		
thing="""
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
"""
print('Incoming...')

for x in statements(thing):
	print('What follows is a statement:')
	print(x)

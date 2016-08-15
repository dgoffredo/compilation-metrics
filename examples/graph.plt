
reset

set terminal png size 768, 1024 nocrop
set output 'graph.png'

unset key

set style data histogram
set style histogram cluster gap 1
set style fill solid border -1

set boxwidth 0.25

set xtics nomirror rotate by 90 right
set x2label 'Source File'
unset x2tics

set ytics nomirror rotate by 90
set ylabel 'Compilation Duration (seconds)'
set yrange [0:*]

plot 'graph.txt' using 2:xticlabel(1)

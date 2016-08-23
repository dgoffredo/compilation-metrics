# Compilation Metrics
Keep track of what's taking so long to compile.

Compilation Metrics has two components: 
* a wrapper script for your compiler that collects statistics on the time and
  resources consumed compiling each file, outputting the collected statistics
  to a database.
* a report generation tool that, provided a markdown file and a description of
  diagrams to produce, renders a website from the statistics database.

## Dependencies
Compilation Metrics is written in python. One goal of the project is to have
as few dependencies as possible, so that it can be used as a drop-in 
replacement for the compiler in most build environments.

Collecting statistics has the following dependencies:
* unix/linux
* python 2.7+
* git (optional)

Report generation has the following additional dependencies:
* gnuplot
* perl

## Usage
TBD
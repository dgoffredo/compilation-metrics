
# Measure resources used by a subprocess. This module assumes that the
# command to be measured will result in the first measurable usage of
# resources by any child process. This practically means that you can
# measure only once, and that you must do so before having created any
# child processes.

# Returns (returnCode, wallTimeDurationSeconds, ResourceUsage)
#
def call(argsList):
    pass # TODO

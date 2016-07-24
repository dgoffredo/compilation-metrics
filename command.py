
from __future__ import print_function

import os

# Wrapper around a list of command line arguments used to invoke the compiler.
# Provides methods for getting the compiler path, output file, source, etc.
#
class Command(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)

    def outputPath(self):
        flag = '-o'
        args = [(i, arg) for i, arg in enumerate(reversed(self)) \
                         if arg.startswith(flag)]
        assert len(args) > 0, 'There are no output-looking arguments.'
        
        i, arg = args[0]
        if arg == flag:
            # The object name follows the arg.
            assert i != 0, 'The last argument is "{}".'.format(flag)
            return self[-i]
        else:
            # The object name is combined with the arg.
            return arg[len(flag):]

    def sourcePath(self):
        assert len(self) > 1, 'Command must have at least two parts.'
        return os.path.abspath(self[-1])

    def compilerPath(self):
        assert len(self) > 0, 'Command is empty.'
        return os.path.abspath(self[0])

    def info(self):
        return {
            'compilerPath': self.compilerPath(),
            'outputPath': self.outputPath(),
            'sourcePath': self.sourcePath()
        }
        
if __name__ == '__main__':
    import sys
    print(Command(sys.argv[1:]).info())

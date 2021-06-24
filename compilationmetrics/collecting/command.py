
from __future__ import print_function

from ..enforce import enforce

import os
from distutils.spawn import find_executable

# Wrapper around a list of command line arguments used to invoke the compiler.
# Provides methods for getting the compiler path, output file, source, etc.
#
class Command(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)

    def getPaths(self):
        try:
            return self.sourcePath(), self.outputPath(), self.compilerPath(), None
        except Exception as error:
            return None, None, None, error

    def without(self, arg_to_omit):
        return Command(arg for arg in self if arg != arg_to_omit)

    def withoutOutputPath(self):
        flag = '-o'
        args = [(i, arg) for i, arg in enumerate(reversed(self)) \
                         if arg.startswith(flag)]
        if len(args) == 0:
            return self

        i, arg = args[0]
        if arg == flag:
            # The object name follows the arg.
            enforce(i != 0, 'The last argument is "{}".'.format(flag))
            return Command(self[:-i-1] + self[-i + 1:])
        else:
            # The object name is combined with the arg.
            return Command(self[:-i-1] + self[-i:])
        
    def withFlag(self, flag):
        args = [self[0]]
        args.append(flag)
        args.extend(self[1:])
        return Command(args)

    def outputPath(self):
        flag = '-o'
        args = [(i, arg) for i, arg in enumerate(reversed(self)) \
                         if arg.startswith(flag)]
        enforce(len(args) > 0, 'There are no output-looking arguments.')

        i, arg = args[0]
        if arg == flag:
            # The object name follows the arg.
            enforce(i != 0, 'The last argument is "{}".'.format(flag))
            return self[-i]
        else:
            # The object name is combined with the arg.
            return arg[len(flag):]

    def sourcePath(self):
        enforce(len(self) > 1, 'Command must have at least two parts.')
        return os.path.abspath(self[-1])
        # TODO gcc (at least certain versions) allows for flags to be
        #      specified after the file name, e.g.
        #          gcc file.c -c -o output.o
        #      Most of the time, though, the last argument is the file to
        #      compile, if there is a file to compile at all.
        
    def compilerPath(self):
        enforce(len(self) > 0, 'Command is empty.')
        return find_executable(self[0])

    def info(self):
        return {
            'compilerPath': self.compilerPath(),
            'outputPath': self.outputPath(),
            'sourcePath': self.sourcePath()
        }

if __name__ == '__main__':
    import sys
    print(Command(sys.argv[1:]).info())

'''
Copyright (c) 2016 David Goffredo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

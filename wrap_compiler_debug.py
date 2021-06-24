#!/usr/bin/env python3

import sys
import wrap_compiler

sys.argv = [sys.argv[0], '--debug'] + sys.argv[1:]
wrap_compiler.main()

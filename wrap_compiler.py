#!/usr/bin/env python3
from compilationmetrics.collecting import collect
import os
import sys


def main():
    if 'COMPILATION_METRICS_DEBUG' in os.environ:
        import json

        def handleMetrics(request):
            print(json.dumps(request, indent=4))
            return collect.writeToDatabase(request)

        sys.exit(
            collect.collect(sys.argv[1:], callback=handleMetrics, debug=True))
    else:
        sys.exit(collect.collect(sys.argv[1:]))


if __name__ == '__main__':
    main()

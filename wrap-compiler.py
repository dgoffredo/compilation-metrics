#!/usr/bin/python
from compilationmetrics.collecting import collect
import sys

if sys.argv.get(1) == '--debug':
    import json

    def handleMetrics(request):
        print(json.dumps(request, indent=4))
        return collect.writeToDatabase(request)

    sys.exit(collect.collect(sys.argv[2:], callback=handleMetrics))
else:
    sys.exit(collect.collect(sys.argv[1:]))
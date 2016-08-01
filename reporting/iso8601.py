
# Parses a subset of ISO 8601 (RFC 3339) without needing dateutil or anything.
# This module uses a regular expression that can parse ISO 8601 datetimes
# matching, for example:
#
#     2016-04-20
#         - April 20th, 2016, no time zone info.
#         - This module will use the local time zone.
#
#     2016-04-20T12:34:32
#         - April 20th, 2016, 12:34:32 PM, no time zone info.
#         - This module will use the local time zone.
#
#     2016-04-20T12:34:32.778943321
#     (or any number of decimal digits)
#         - April 20th, 2016, 12:34 PM and 32.778943321 seconds, no time zone info.
#         - This module will use the local time zone.
#
#     2016-04-20-05:00
#         - April 20th, 2016, relative to UTC-05:00, i.e. EST without DST.
#
#     2016-04-20T12:34:32-05:00
#         - April 20th, 2016, 12:34:32 PM, relative to UTC-05:00.
#
#     2016-08-01T05:44:37.756547Z
#         - August 1st, 2016, 5:44 AM and 37.756547 seconds, relative to UTC.
#

import datetime, time, re

class NaiveTzinfo(datetime.tzinfo):
    def __init__(self, hourPart=0, minutePart=0, delta=None):
        if delta is not None:
            self.delta = delta
        else:
            self.delta = datetime.timedelta(minutes=minutePart, hours=hourPart)

    def utcoffset(self, dt):
        return self.delta # 'dt' is ignored.

    def dst(self, dt):
        return None # Not known 

    def tzname(self, dt):
        return None # Not known

def currentNaiveTzinfo():
    nowUnix = time.time()
    dt = datetime.datetime
    delta = dt.fromtimestamp(nowUnix) - dt.utcfromtimestamp(nowUnix)
    return NaiveTzinfo(delta=delta)

def makeRegexGetter():
    iso8601RegexPattern = r'^\s*(?P<year>\d\d\d\d)-' + \
                          r'(?P<month>\d\d)-' + \
                          r'(?P<day>\d\d)' + \
                          r'(T(?P<hour>\d\d):' + \
                          r'(?P<minute>\d\d):' + \
                          r'(?P<second>\d\d)' + \
                          r'(?P<fraction>\.\d+)?)?' + \
                          r'(?P<tz>Z|(?P<tzSign>\+|-)' + \
                          r'(?P<tzHour>\d\d)' + \
                          r'(:(?P<tzMinute>\d\d))?)?\s*$'
    regex = re.compile(iso8601RegexPattern)
    def getter():
        return regex
    return getter

regex = makeRegexGetter()

# Returns a datetime.datetime instance.
# If a timezone is not specified, the local timezone is assumed.
#
def parse(iso8601String):
    match = regex().match(iso8601String)
    assert match, 'Invalid (or unsupported) ISO8601: {}'.format(iso8601String)
    groups = match.groupdict()

    if groups['tz'] is None:
        tz = currentNaiveTzinfo() # local
    elif groups['tz'].upper() == 'Z':
        tz = NaiveTzinfo() # UTC
    else:
        tzSign = -1 if groups['tzSign'] == '-' else 1
        tz = NaiveTzinfo(tzSign * int(groups['tzHour']), int(groups['tzMinute']))

    def asInt(name):
        return int(groups[name])

    def zeroOr(name, constructor=int):
        if groups[name] is None:
            return 0
        return constructor(groups[name])

    year = asInt('year')
    month = asInt('month')
    day = asInt('day')
    hour = zeroOr('hour')
    minute = zeroOr('minute')
    second = zeroOr('second')
    microsecond = int(zeroOr('fraction', float) * 10e6)

    return datetime.datetime(year, month, day, hour, minute, second, microsecond, tz)

if __name__ == '__main__':
    import sys
    for line in sys.stdin:
        print(parse(line))
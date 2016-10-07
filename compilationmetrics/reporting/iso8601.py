
# Parses a subset of ISO 8601 (RFC 3339) without needing dateutil or anything.
# This module uses a regular expression that can parse ISO 8601 datetimes
# matching, for example:
#
#     2016-04-20
#         - April 20th, 2016, no time zone info.
#         - This module will use the local time zone and convert to UTC.
#
#     2016-04-20T12:34:32
#         - April 20th, 2016, 12:34:32 PM, no time zone info.
#         - This module will use the local time zone and convert to UTC.
#
#     2016-04-20T12:34:32.778943321
#     (or any number of decimal digits)
#         - April 20th, 2016, 12:34 PM and 32.778943321 seconds, no time zone info.
#         - This module will use the local time zone and convert to UTC.
#
#     2016-04-20-05:00
#         - April 20th, 2016, relative to UTC-05:00, i.e. EST without DST.
#         - This module will convert to UTC
#
#     2016-04-20T12:34:32-05:00
#         - April 20th, 2016, 12:34:32 PM, relative to UTC-05:00.
#         - This module will convert to UTC
#
#     2016-08-01T05:44:37.756547Z
#         - August 1st, 2016, 5:44 AM and 37.756547 seconds, in UTC.
#
#     TODO Add time duration examples.
#
# ******************************************************
# * All datetime.datetime objects are returned in UTC. *
# ******************************************************
#

import datetime, time, re
from ..enforce import enforce

# utcDatetime + currentOffset() == localDatetime
#
# and so,
#
# localDatetime - currentOffset() == utcDatetime
# 
def currentOffset():
    nowUnix = time.time()
    dt = datetime.datetime
    return dt.fromtimestamp(nowUnix) - dt.utcfromtimestamp(nowUnix)

# Lazy loading of compiled regex
#
class LazyRegex(object):
    def __init__(self, pattern):
        self._pattern = pattern
        self._regex = None
    
    def __call__(self):
        if self._regex is None:
            self._regex = re.compile(self._pattern)
        return self._regex

datetimeRegex = LazyRegex(r'^\s*(?P<year>\d\d\d\d)-' + \
                          r'(?P<month>\d\d)-' + \
                          r'(?P<day>\d\d)' + \
                          r'(T(?P<hour>\d\d):' + \
                          r'(?P<minute>\d\d):' + \
                          r'(?P<second>\d\d)' + \
                          r'(?P<fraction>\.\d+)?)?' + \
                          r'(?P<tz>Z|(?P<tzSign>\+|-)' + \
                          r'(?P<tzHour>\d\d)' + \
                          r'(:(?P<tzMinute>\d\d))?)?\s*$')


''' ISO8601 time durations, from Wikipedia:
       1. PnYnMnDTnHnMnS
       2. PnW
       3. P<date>T<time> 
   But I'll be supporting only the first two.
'''
durationRegex = LazyRegex(r'P((?P<weeks>\d+(\.\d+)?)W|' + \
                          r'((?P<years>\d+(\.\d+)?)Y)?' + \
                          r'((?P<months>\d+(\.\d+)?)M)?' + \
                          r'((?P<days>\d+(\.\d+)?)D)?' + \
                          r'(T' + \
                          r'((?P<hours>\d+(\.\d+)?)H)?' + \
                          r'((?P<minutes>\d+(\.\d+)?)M)?' + \
                          r'((?P<seconds>\d+(\.\d+)?)S)?' + \
                          r')?)')
                      
# Returns a datetime.datetime instance.
# If a timezone is not specified, the local timezone is assumed.
#
def _makeDatetime(match):
    groups = match.groupdict()

    if groups['tz'] is None:
        offset = currentOffset() # local
    elif groups['tz'].upper() == 'Z':
        offset = datetime.timedelta() # UTC
    else:
        tzSign = -1 if groups['tzSign'] == '-' else 1
        offset = datetime.timedelta(hours=tzSign*int(groups['tzHour']),
                                    minutes=int(groups['tzMinute']))

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
    microsecond = int(round(zeroOr('fraction', float) * 10e6))

    d = datetime.datetime(year, month, day, hour, minute, second, microsecond)
    
    # *subtract* the offset so that the representation goes from whatever
    # whatever local time into UTC. The offset is the offset *from* uTC,
    # and so -offset is the offset *to* UTC.
    return d - offset

# Note that if 'years' or 'months' exist in the specified 'match', the
# returned 'datetime.timedelta' will be an approximation of the ISO 8601
# duration, because counting months and years depends on from when one
# counts. Here, one year is 365 days, and one month is 30.42 days.
#
def _makeTimedelta(match):
    parts = { name: float(value) \
              for name, value in match.groupdict().iteritems() \
              if value is not None}
    
    # Years and months don't exist in datetime.timedelta's constructor,
    # so translate them into days so that 'groups' can be expanded as
    # keyword arguments into the returned timedelta's constructor.
    #
    years = parts.get('years')
    if years is not None:
        parts['days'] = parts.get('days', 0) + 365 * years
        del parts['years']

    months = parts.get('months')
    if months is not None:
        parts['days'] = parts.get('days', 0) + 30.42 * months
        del parts['months']

    return datetime.timedelta(**parts)

# Returns either a datetime.datetime or a datetime.timedelta, depending on
# the format of the specified 'iso8601String'. For datetimes, uses local time
# zone if no time zone is specified, but the resulting datetime.datetime is
# expressed in UTC.
# See _makeDatetime and _makeTimedelta.
#
def parse(iso8601String):
    s = iso8601String

    match = datetimeRegex().match(s)
    if match:
        return _makeDatetime(match)

    match = durationRegex().match(s)
    enforce(match, 'Invalid (or unsupported) ISO 8601: {}'.format(s))
    if match:
        return _makeTimedelta(match)

if __name__ == '__main__':
    import sys
    for line in sys.stdin:
        print(parse(line))
            
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

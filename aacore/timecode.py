# This file is part of Active Archives.
# Copyright 2006-2011 the Active Archives contributors (see AUTHORS)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Also add information on how to contact you by electronic and paper mail.


import math
import re

# timecode_pat = re.compile(r"(\d+):(\d+):(\d+)(?:[.,](\d+))?")
timecode_pat = re.compile(r"(?:(\d+):)?(\d+):(\d+)(?:[.,](\d+))?")


def timecode_fromsecs(rawsecs, fract=True, alwaysfract=False, 
                      fractdelim=',', alwayshours=False):
    """ Returns a string in HH:MM:SS[.xxx] notation if fract is True, uses .xxx
    if either necessary (non-zero) OR alwaysfract is True
    """
    hours = math.floor(rawsecs / 3600)
    rawsecs -= hours * 3600
    mins = math.floor(rawsecs / 60)
    rawsecs -= mins * 60
    if fract:
        secs = math.floor(rawsecs)
        rawsecs -= secs
        if (rawsecs > 0 or alwaysfract):
            fract = "%.03f" % rawsecs
            if hours or alwayshours:
                return "%02d:%02d:%02d%s%s" % (hours, mins, secs, fractdelim, \
                        fract[2:])
            else:
                return "%02d:%02d%s%s" % (mins, secs, fractdelim, fract[2:])
        else:
            if hours or alwayshours:
                return "%02d:%02d:%02d" % (hours, mins, secs)
            else:
                return "%02d:%02d" % (mins, secs)

    else:
        secs = round(rawsecs)
        if hours or alwayshours:
            return "%02d:%02d:%02d" % (hours, mins, secs)
        else:
            return "%02d:%02d" % (mins, secs)


def timecode_tosecs(tcstr):
    try:
        r = timecode_pat.search(tcstr)
    except TypeError:
        return None
    if r:
        ret = 0
        if r.group(1):
            ret += 3600 * int(r.group(1))
        ret += 60 * int(r.group(2))
        ret += int(r.group(3))
        if (r.group(4)):
            ret = float(str(ret) + "." + r.group(4))
        return ret
    else:
        return None


def parse2secs(val):
    try:
        return float(val)
    except ValueError:
        return timecode_tosecs(val)
## to accept None
#    except TypeError:
#        return

if __name__ == "__main__":
    def t(x):
        # with fraction
        s = timecode_fromsecs(x, True, False)
        print x, "=>", s, "=>", timecode_tosecs(s)
        # without fraction
        s = timecode_fromsecs(x, False)
        print x, "=>", s, "=>", timecode_tosecs(s)

    t(0)
    t(59.666666666666666)
    t(60)
    t(60.0)
    t(1235 / 3.0)
    t(10000.5)

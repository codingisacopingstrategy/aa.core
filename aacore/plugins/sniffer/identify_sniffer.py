# This file is part of Active Archives.
# Copyright 2006-2010 the Active Archives contributors (see AUTHORS)
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


import os, sys, re, subprocess # import Popen, PIPE, STDOUT

from aacore.settings import IDENTIFY
import sniffer
from aacore.mdx import get_markdown


class IdentifySniffer (sniffer.Sniffer):
    @classmethod
    def sniff(cls, url, rfile, data):
        #if not data['content_type'].startswith('image/'):
            #return None
        out = system_stdin_stderr(IDENTIFY + ' -verbose "%s"' % url)
        md = get_markdown()
        return "<pre>%s</pre>" % md.convert(markup(out))

def system_stdin_stderr (cmd, readlimitbytes=4000):
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    (pin, pout) = (p.stdin, p.stdout)
    results = pout.read(readlimitbytes)
    pin.close(); pout.close()
    os.kill(p.pid, 1)
    return results

def streamInfoGetComponent (sinfo, cname):
    for rec in sinfo:
        if (rec[0] == cname): return rec[1]

def streamInfoGetVideoSize (sinfo):
    vidinfo = streamInfoGetComponent(sinfo, 'video')
    if (vidinfo != None):
        parts = vidinfo.split(",")
        for part in parts:
            part = part.strip()
            if part.find('x') >= 0:
                ret = part.split("x")[:2]
                return map(lambda x: int(x), ret)
    return (-1, -1)


def markup (text):
    size_match = re.search(r"Geometry:\ (?P<width>\d+)x(?P<height>\d+)", text, flags=re.X|re.I)
    output = ""
    if size_match:
        output += text[:size_match.start()]
        output += "Geometry: [[width::%(width)s]]x[[height::%(height)s]]" % size_match.groupdict()
        output +=text[size_match.end():]
    return output


if (__name__ == "__main__"):
    import sys
    src = sys.argv[1]
    out = system_stdin_stderr(IDENTIFY + ' -i "%s"' % src)
    print markup(out)

#    mi = getStreamInfo(src)
#    print mi


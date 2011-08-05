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
import sniffer, aacore.wikilinks


class IdentifySniffer (sniffer.Sniffer):
    @classmethod
    def sniff(cls, url, rfile, data):
        #if not data['content_type'].startswith('image/'):
            #return None
        out = system_stdin_stderr(IDENTIFY + ' -verbose "%s"' % url)
        #return "<pre>%s</pre>" % markup(out)
        return "<pre>%s</pre>" % aacore.wikilinks.markup(markup(out))

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

def getStreamInfo (path):
    ret = {}
    results = system_stdin_stderr('-i "%s"' % path)
    duration = 0
    
    for line in results.splitlines():
        line = line.strip().lower()

        results = re.search("duration:\s*(\d\d):(\d\d):(\d\d)\.(\d+)?", line, re.IGNORECASE)
        if results:
            results = results.groups()
            duration = (int(results[0]) * 60 * 60) + (int(results[1]) * 60) + int(results[2])
            if len(results) > 3:
                duration = float(str(duration)+"."+results[3])
            else:
                duration = float(duration)

        results = re.search(r"stream #(\d+)\.(\d+).*(audio|video): (.*)", line, re.IGNORECASE)
        if results:
            results = results.groups()
            stream_num = int(results[1])
            type = results[2]
            info = results[3]
            ret[type] = info
            
    # FURTHER EXTRACT DATA
    # DURATION
    if (duration > 0.0): ret['duration'] = duration
    
    # VIDEO
    if ret.has_key('video'):
        # SIZE (width, height)
        sizepat = r"(\d+)x(\d+),?\s*"
        r = re.search(sizepat, ret['video'])
        if r:
            ret['width'] = int(r.group(1))
            ret['height'] = int(r.group(2))
        # remove the size from the video info string
        ret['video'] = re.sub(sizepat, "", ret['video'])
    
        # FRAMERATE (fps)
        fpspat = r"(\d+(\.\d+)?)\s*fps(\(.*\))?\s*"
        r = re.search(fpspat, ret['video'])
        if r:
            ret['fps'] = float(r.group(1))
        # remove the size from the video info string
        ret['video'] = re.sub(fpspat, "", ret['video'])
        # cleanup
        ret['video'] = ret['video'].strip(" ,")

    return ret

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


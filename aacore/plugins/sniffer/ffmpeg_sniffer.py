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

from aacore.settings import FFMPEG
import sniffer
from aacore.mdx import get_markdown

class FFMpegSniffer (sniffer.Sniffer):
    @classmethod
    def sniff(cls, url, rfile, data):
        # TODO: find the accepted mimetypes for this sniffer
        #       and uncomment below
        #if data['content_type'] is not in ["video/mpeg"]:
            #return None
        out = system_stdin_stderr(FFMPEG + ' -i "%s"' % url)
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
    # duration
    text = re.sub(
        r"(?P<PRE>duration: \s*) (?P<HOUR>\d\d): (?P<MIN>\d\d): (?P<SECS>\d\d(\.(\d+))?)",
        "\g<PRE>[[duration::\g<HOUR>:\g<MIN>:\g<SECS>]]",
        text, flags=re.X|re.I)

    # bitrate (kb/s)
    text = re.sub(
        r"(?P<PRE>bitrate: \s*) (?P<bitrate>\d+) \s* kb/s",
        "\g<PRE>[[bitrate::\g<bitrate>]] kb/s",
        text, flags=re.X|re.I)

    # VIDEOINFO (Stream 0.x: Video: ...)
    # videoinfo, width, height, fps
    videoline_match = re.search(r"^ \s* Stream .*: \s+ Video: .* $", text, flags=re.M|re.X|re.I)
    if videoline_match:
        videoline = videoline_match.group(0)
        videoinfo_match = re.search(r"Video: \s* (?P<videoinfo>.*)", videoline, flags=re.I|re.X)
        if videoinfo_match:
            videoinfo = videoinfo_match.group(1)
            videoinfo = "[[videoinfo:: %s]]" % videoinfo
            
            size_match = re.search(r"(?P<width>\d+)x(?P<height>\d+) \s* ,? \s*", videoinfo, flags=re.X|re.I)
            if size_match:
                # remove match from videoinfo & append the markup
                videoinfo = videoinfo[:size_match.start()] + videoinfo[size_match.end():]
                videoinfo += ", [[width::%(width)s]]x[[height::%(height)s]]" % size_match.groupdict()

            fps_match = re.search(r"(?P<fps>\d+) \s* fps,? \s*", videoinfo, flags=re.X|re.I)
            if fps_match:
                # remove match from videoinfo & append the markup
                videoinfo = videoinfo[:fps_match.start()] + videoinfo[fps_match.end():]
                videoinfo += ", [[fps::%(fps)s]] fps" % fps_match.groupdict()
            # wrap videoinfo
            videoline = videoline[:videoinfo_match.start(1)] + videoinfo + videoline[videoinfo_match.end(1):]
        # SUB
        text = text[:videoline_match.start()] + videoline + text[videoline_match.end():]
            
    # AUDIOINFO (Stream 0.x: Audio: ...)
    # markup: audioinfo, audiorate, audiochannels
    audioline_match = re.search(r"^ \s* Stream .*: \s+ Audio: .* $", text, flags=re.M|re.X|re.I)
    if audioline_match:
        audioline = audioline_match.group(0)
        audioinfo_match = re.search(r"Audio: \s* (?P<audoinfo>.*)", audioline, flags=re.I|re.X)
        if audioinfo_match:
            audioinfo = audioinfo_match.group(1)
            audioinfo = "[[audioinfo:: %s]]" % audioinfo
            
            rate_match = re.search(r"(?P<audiorate>\d+) \s* Hz \s* ,? \s*", audioinfo, flags=re.X|re.I)
            if rate_match:
                # remove match from videoinfo & append the markup
                audioinfo = audioinfo[:rate_match.start()] + audioinfo[rate_match.end():]
                audioinfo += ", [[audiorate::%(audiorate)s]] Hz" % rate_match.groupdict()

            channels_match = re.search(r"(?P<channels>mono|stereo) \s* ,? \s*", audioinfo, flags=re.X|re.I)
            if channels_match:
                # remove match from videoinfo & append the markup
                audioinfo = audioinfo[:channels_match.start()] + audioinfo[channels_match.end():]
                audioinfo += ", [[audiochannels::%(channels)s]]" % channels_match.groupdict()

            audioline = audioline[:audioinfo_match.start(1)] + audioinfo + audioline[audioinfo_match.end(1):]
        # SUB
        text = text[:audioline_match.start()] + audioline + text[audioline_match.end():]

    # METADATA


    return text

#    video = re.search(r"^ \s* Stream .*: \s+ Video: (?P<VIDINFO>.*) .* (?P<SIZE>\d+x\d+) .* (?P<FPS>\d+fps)? .* $", text, flags=re.M|re.X|re.I)

    # AUDIO STREAM
    audio = re.search(r"^ \s* Stream .*: \s+ Audio: (?P<content>.*) $", text, flags=re.M|re.X|re.I)
    if audio:    
        audio = audio.group(0)

    return text

if (__name__ == "__main__"):
    import sys
    src = sys.argv[1]
    out = system_stdin_stderr(FFMPEG + ' -i "%s"' % src)
    print markup(out)

#    mi = getStreamInfo(src)
#    print mi


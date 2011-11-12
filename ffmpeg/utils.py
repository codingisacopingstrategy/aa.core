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

try:
    from settings import FFMPEG
except ImportError:
    FFMPEG = "ffmpeg"

def system_stdin_stderr (cmd, readlimitbytes=4000):
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    (pin, pout) = (p.stdin, p.stdout)
    results = pout.read(readlimitbytes)
    pin.close(); pout.close()
    os.kill(p.pid, 1)
    return results

meta_pat = re.compile(r"(?P<key>\S+)\s*\:\s*(?P<value>.+)", re.I)

def ffmpeg_get_info (path):
    """
    Returns: a dictionary of audio/video data such as returned by ffmpeg -i
    the keys audio & video are the "raw" information that ffmpeg provides and their presence
    indicates if ffmpeg detected an audio / video stream

    Example output:

    {'audio': 'vorbis, 44100 hz, mono, s16, 60 kb/s',
     'audio_bitrate': '60',
     'audio_channels': 1,
     'audio_codec': 'vorbis',
     'audio_rate': '44100',
     'duration': 29.53,
     'fps': 30.0,
     'height': 480,
     'video': 'theora, yuv420p, 640x480, 30 fps, 30 tbr, 30 tbn, 30 tbc',
     'video_codec': 'theora',
     'width': 640}

    """

    ret = {}
    results = system_stdin_stderr('{0} -i "{1}"'.format(FFMPEG, path))

    duration = 0
    meta = {}
    seek_meta = False

    for line in results.splitlines():
        ## NB: forces all lower case here!?
        # line = line.strip().lower()

        results = re.search("duration:\s*(\d\d):(\d\d):(\d\d)\.(\d+)?", line, re.I)
        if results:
            results = results.groups()
            duration = (int(results[0]) * 60 * 60) + (int(results[1]) * 60) + int(results[2])
            if len(results) > 3:
                duration = float(str(duration)+"."+results[3])
            else:
                duration = float(duration)

        results = re.search(r"stream #(\d+)\.(\d+).*(audio|video): (.*)", line, re.I)
        if results:
            results = results.groups()
            stream_num = int(results[1])
            type = results[2].lower()
            info = results[3]
            ret[type] = info

        if not seek_meta:
            if "metadata:" in line.lower():
                seek_meta = True
        else:
            m = meta_pat.search(line)
            if m:
                d = m.groupdict()
                meta[d.get("key").lower()] = d.get("value").strip()

    if meta:
        ret['meta'] = meta

    # FURTHER EXTRACT DATA
    # DURATION
    if (duration > 0.0): ret['duration'] = duration
    
    # VIDEO
    if ret.has_key('video'):
        info = ret['video']
        # Codec
        m = re.search(r"(?P<codec>\w+)", info)
        if m:
            ret['video_codec'] = m.groupdict().get("codec")

        # frame size (width, height)
        m = re.search(r"(?P<width>\d+)x(?P<height>\d+),?\s*", info)
        if m:
            d = m.groupdict()
            ret['width'] = int(d.get("width"))
            ret['height'] = int(d.get("height"))
    
        # framerate (fps)
        m = re.search(r"(?P<fps>\d+(\.\d+)?)\s?((fps)|(tbr))", info)
        if m:
            ret['fps'] = float(m.groupdict().get("fps"))

    # AUDIO
    if ret.has_key('audio'):
        info = ret['audio']
        # audio_codec
        m = re.search(r"(?P<codec>\w+)", info)
        if m:
            ret['audio_codec'] = m.groupdict().get("codec")

        # sample rate
        m = re.search(r"(?P<srate>\d+)\s?hz", info, flags=re.I)
        if m:
            ret['audio_sampling_rate'] = m.groupdict().get("srate")

        # audio_bits (sample depth, e.g. 8, 16, 24)
        m = re.search(r"\bs(?P<bits>\d+)\b", info)
        if m:
            ret['audio_bits'] = m.groupdict().get("bits")

        # audio_bitrate
        m = re.search(r"(?P<bitrate>\d+)\s?kb/s\b", info)
        if m:
            ret['audio_bitrate'] = m.groupdict().get("bitrate")

        # audio_channels
        if "stereo" in info:
            ret['audio_channels'] = 2
        elif "mono" in info:
            ret['audio_channels'] = 1

    return ret

#if (__name__ == "__main__"):
#    pass


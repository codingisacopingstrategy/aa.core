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

import re, urllib2, datetime, email.utils, urlparse, os

from aacore.settings import USER_AGENT


# http://code.activestate.com/recipes/577015-parse-http-date-time-string/
def parse_http_datetime(s):
    return datetime.datetime(*email.utils.parsedate(s)[:6])


# http://www.artima.com/forums/flat.jsp?forum=122&thread=15024
class NotModifiedHandler(urllib2.BaseHandler):
    def http_error_304(self, req, fp, code, message, headers):
        addinfourl = urllib2.addinfourl(fp, headers, req.get_full_url())
        addinfourl.code = code
        return addinfourl


def splitContentType(t):
    m = splitContentType.pat.match(t)
    if m:
        d = m.groupdict()
        (mt, charset) = (d['mimetype'], d['charset'])
        if charset == None:
            charset = ""
        return (mt, charset)
splitContentType.pat = re.compile(r"""\s*(?P<mimetype>[\w+_-]+/[\w+_-]+)\s*(?:;\s*charset=(?P<charset>[\w-]*)\s*)?""")


def conditional_get(url, last_modified=None, etag=None):
    """
    Uses optional last_modified and/or etag to do a "conditional get" of the given url.
    (when neither is given, results in a regular get)
    Returns: file-like object as returned by urllib2.urlopen
    """
    request = urllib2.Request(url)
    request.add_header("User-Agent", USER_AGENT)
    if last_modified:
        request.add_header("If-Modified-Since", last_modified)
    if etag:
        request.add_header("If-None-Match", etag)
    opener = urllib2.build_opener(NotModifiedHandler())
    return opener.open(request)


class ResourceOpener():
    """
    ResourceOpener simply deals with Conditional GET, and normalizes common headers
    Interesting attributes: original_url, url, file, info, status, content_type, charset, content_length
    """
    def __init__(self, url):
        self.original_url = url
        self.info = {}

    def get(self, last_modified=None, etag=None):
        f = conditional_get(self.original_url, last_modified, etag)
        self.file = f
        self.url = f.geturl()
        if hasattr(f, 'code'):
            self.status = f.code
            if self.status == 304:
                return self.status
        else:
            self.status = None

        self.info = f.info()
        self.original_url = self.original_url
        self.content_type = self.info.get('content-type', '').lower()
        (self.content_type, self.charset) = splitContentType(self.content_type)

        try:
            self.content_length = long(self.info.get('content-length', 0))
        except ValueError:
            self.content_length = 0

        self.last_modified_raw = self.info.get("Last-Modified", "")
        if self.last_modified_raw:
            self.last_modified = parse_http_datetime(self.last_modified_raw)
        else:
            self.last_modified = None

        self.etag = self.info.getheader("ETag", "")

        # filename / extension
        path = urlparse.urlparse(self.url).path
        (path, filename) = os.path.split(path)
        self.filename = filename
        (base, ext) = os.path.splitext(filename)
        self.ext = ext.lower()

        return self.status

    def writeToFile(self, outfile, verbose=False):
        try:
            request = urllib2.Request(self.url)
            request.add_header("User-Agent", USER_AGENT)
            requestfile = urllib2.urlopen(request)

            bytes = 0
            total = long(requestfile.info().get("content-length", -1))
            lastprogress = 0
            while True:
                data = requestfile.read(1024)
                if not data:
                    break
                bytes += len(data)
                outfile.write(data)
                if total:
                    progress = int(100 * (float(bytes) / total))
                    if progress != lastprogress:
                        if verbose:
                            print "\t%d%% completed (%d/%d)..." % (progress, bytes, total)
                        lastprogress = progress
            if verbose:
                print "\tWrote %d bytes to %s" % (bytes, cpath)
            outfile.close()
            return bytes

        except ValueError, e:
            return -1  # Bad URL
        except urllib2.HTTPError, e:
            return -1


if __name__ == "__main__":
    url1 = "http://ubu.artmob.ca/sound/burroughs_william/Break-Through/Burroughs-William-S_01-K-9.mp3"
    url2 = "http://www.youtube.com/watch?v=rUJF6ke1SoE"
    r1 = ResourceOpener(url1)
    r2 = ResourceOpener(url2)
    print r1.get()
    print r2.get()

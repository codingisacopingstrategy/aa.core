# HTTP utilities
# (conditional get, dealing with parsing http headers)
#
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
#
#


# TODO: Rename HttpUtils ?


"""
Utilities to deal with conditional GET built on top of urllib2.
"""


import re
import urllib2
import datetime
import email.utils
import urlparse
import os


USER_AGENT = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1) Gecko/20090624 Firefox/3.5"


def parse_http_datetime(string):
    """
    Parses datetime strings returned by HTTP servers and returns datetime
    instances.
    
    It supports the three datetime formats defined in the RFC 2616 standard.

    >>> rcf_822 = "Sun, 06 Nov 1994 08:49:37 GMT"
    >>> print(parse_http_datetime(rcf_822))
    1994-11-06 08:49:37

    >>> rcf_850 = "Sunday, 06-Nov-94 08:49:37 GMT"
    >>> print(parse_http_datetime(rcf_850))
    1994-11-06 08:49:37

    >>> asctime = "Sun Nov  6 08:49:37 1994"
    >>> print(parse_http_datetime(asctime))
    1994-11-06 08:49:37

    Taken from http://code.activestate.com/recipes/577015-parse-http-date-time-string/
    """
    return datetime.datetime(*email.utils.parsedate(string)[:6])


class NotModifiedHandler(urllib2.BaseHandler):
    """
    Implements an error handler for 304 response code (Not Modified) and Fakes
    URL-handle so that we can process the result of the open() like it were a
    usual request.

    Urllib2 only ever returns a response if the code is 200. In other cases,
    HTTPError exceptions are raised.

    Taken from http://www.artima.com/forums/flat.jsp?forum=122&thread=15024
    """
    def http_error_304(self, req, fp, code, message, headers):
        addinfourl = urllib2.addinfourl(fp, headers, req.get_full_url())
        addinfourl.code = code
        return addinfourl


def split_content_type(ct):
    """
    Parses the HTTP response Content-Type entity-header field and returns a
    tuple contening the content-type and the media-type.

    >>> ct = "image/jpeg"
    >>> print(split_content_type(ct))
    ('image/jpeg', '')

    >>> ct = "text/html; charset=iso-8859-1"
    >>> print(split_content_type(ct))
    ('text/html', 'iso-8859-1')
    """
    content_type_re = re.compile(r"""\s*(?P<mimetype>[\w+_-]+/[\w+_-]+)\s*(?:;\s*charset=(?P<charset>[\w-]*)\s*)?""")
    m = content_type_re.match(ct)
    if m:
        d = m.groupdict()
        (mt, charset) = (d['mimetype'], d['charset'])
        if charset == None:
            charset = ""
        return (mt, charset)


def conditional_get(url, last_modified=None, etag=None):
    """
    Does a "conditional get" of the given URL using optional last_modified
    and/or etag arguments, or a regular get if neither is given. Returns a
    file-like object as returned by urllib2.urlopen.

    >>> url = "http://ubu.artmob.ca/sound/burroughs_william/Break-Through/Burroughs-William-S_01-K-9.mp3"
    >>> last_modified = "2007-05-31 21:19:04"
    >>> etag = "542a57-129bfaf-431caa5f08200"
    >>> page = conditional_get(url, last_modified, etag)
    >>> print(page.code)
    200
    >>> print(page.msg)
    OK
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

    >>> url1 = "http://ubu.artmob.ca/sound/burroughs_william/Break-Through/Burroughs-William-S_01-K-9.mp3"
    #>>> url2 = "http://www.youtube.com/watch?v=rUJF6ke1SoE"
    >>> r1 = ResourceOpener(url1)
    #>>> r2 = ResourceOpener(url2)
    >>> print(r1.get())
    #>>> print(r2.get())
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
        #self.original_url = self.original_url
        self.content_type = self.info.get('content-type', '').lower()
        (self.content_type, self.charset) = split_content_type(self.content_type)

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
            request = urllib2.Request(self.original_url)
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
                print "\tWrote %d bytes to %s" % (bytes, outfile)
            outfile.close()
            return bytes

        except ValueError:
            return -1  # Bad URL
        except urllib2.HTTPError:
            return -1


if __name__ == "__main__":
    import doctest
    doctest.testmod()

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


"""
docstring :)
"""

import urllib2
import urlparse
import lxml
import lxml.cssselect
import html5lib


def spider(url, levels=1, user_agent=None):
    """
    Spiders the given url and returns a dictionnary containing all its links
    and images. Takes an optional depth as second argument (not implemented yet).
    """
    ret = {}

    request = urllib2.Request(url)
    if user_agent:
        request.add_header("User-Agent", user_agent)
    f = urllib2.urlopen(request)
    parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"), 
                                 namespaceHTMLElements=False)
    page = parser.parse(f)

    seen = {}
    for elt in lxml.cssselect.CSSSelector('a[href]')(page):
        href = urlparse.urljoin(f.geturl(), elt.attrib['href'])
        if href.startswith('http'):
            if not href in seen:
                seen[href] = True
    ret['links'] = seen.keys()
    ret['links'].sort()

    seen = {}
    for elt in lxml.cssselect.CSSSelector('img[src]')(page):
        src = urlparse.urljoin(f.geturl(), elt.attrib['src'])
        if src.startswith('http'):
            if not src in seen:
                seen[src] = True
    ret['images'] = seen.keys()
    ret['images'].sort()

    return ret


if __name__ == "__main__":
    import sys, pprint
    pprint.pprint(spider(sys.argv[1]))

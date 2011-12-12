import re
import rdfutils
import subprocess
import os.path
import feedparser
from urlparse import urlparse
from utils import get_rdf_model
from aacore.models import Resource
from textwrap import dedent
from django.conf import settings


class AAFilter(object):
    def __init__(self, arguments, stdin):
        self.arguments = arguments or ""
        self.parsed_arguments = {}
        self.stdin = stdin
        self.stdout = None
        if self.validate():
            return self.run()

    def validate(self):
        return True

    @staticmethod
    def uri_to_path(uri):
        return urlparse(uri).path

    def get_next_path(self):
        extension = os.path.splitext(self.stdin)[1]
        return "%s|%s:%s%s" % (self.stdin, self.__class__.__name__, 
                               self.arguments, extension)


class AAFilterEmbed(AAFilter):
    name = "embed"

    def run(self):
        embed_style = None
        if self.arguments:
            embed_style = self.arguments
        else:
            url = Resource.get_url_from_local_path(self.stdin)
            q = dedent("""\
                PREFIX dc:<http://purl.org/dc/elements/1.1/>
                PREFIX aa:<http://activearchives.org/terms/>
                PREFIX http:<http://www.w3.org/Protocols/rfc2616/>
                PREFIX media:<http://search.yahoo.com/mrss/>
                
                SELECT ?ctype ?format ?audiocodec ?videocodec
                WHERE {{
                  OPTIONAL {{ <%(URL)s> http:content_type ?ctype . }}
                  OPTIONAL {{ <%(URL)s> dc:format ?format . }}
                  OPTIONAL {{ <%(URL)s> media:audio_codec ?audiocodec . }}
                  OPTIONAL {{ <%(URL)s> media:video_codec ?videocodec . }}
                }}""".strip() % {'URL': url})

            model = get_rdf_model()

            b = {}
            for row in rdfutils.query(q, model):
                for name in row:
                    b[name] = rdfutils.rdfnode(row.get(name))
                break

            stdout = ""

            # TODO: move to templates
            if b.get('ctype') in ("image/jpeg", "image/png", "image/gif"):
                embed_style = "img"
            elif b.get('ctype') in ("video/ogg", "video/webm") or (b.get('videocodec') in ("theora", "vp8")):
                embed_style = "html5video"
            elif b.get('ctype') in ("audio/ogg", ) or (b.get('audiocodec') == "vorbis" and (not b.get('videocodec'))):
                embed_style = "html5audio"
            elif b.get('ctype') in ("text/html", ):
                embed_style = "iframe"
            elif b.get('ctype') in ("application/rss+xml", "text/xml", "application/atom+xml"):
                embed_style = "feed"
            else:
                embed_style = None 

        # TODO: move to templates
        if embed_style == "img":
            stdout = '<img src="%s" />' % self.stdin
        elif embed_style == "html5video":
            stdout = '<video class="player" controls src="%s" />' % self.stdin
        elif embed_style == "html5audio":
            stdout = '<audio class="player" controls src="%s" />' % self.stdin
        elif embed_style == "iframe":
            stdout = '<iframe src="%s"></iframe>' % self.stdin
        elif embed_style == "feed":
            feed = feedparser.parse(settings.DIRNAME + self.stdin)
            stdout = u''
            for entry in feed['entries'][:4]:
                stdout += u'<div>'
                stdout += u'<h3><a href="%s">%s</a></h3>' % (entry.link, entry.title)
                stdout += u'<div>'
                stdout += entry.summary
                stdout += u'</div>'
                stdout += u'</div>'
        else:
            stdout = "<p>Unable to detect embed type</p>"

        self.stdout = stdout


class AAFilterBW(AAFilter):
    name = "bw"
    def run(self):
        stdout = settings.DIRNAME + self.get_next_path()
        if not os.path.exists(stdout):
            cmd = 'convert -colorspace gray %s %s' % (settings.DIRNAME + self.stdin, 
                                                      stdout)
            p1 = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE, 
                                  stdin=subprocess.PIPE)
            (stdout_data, stderr_data) = p1.communicate(input=self.stdin)
        self.stdout = stdout


class AAFilterResize(AAFilter):
    name = "resize"

    def validate(self):
        sizepat = re.compile(r"(?P<width>\d+)px", re.I)
        match = sizepat.match(self.arguments)
        if match:
            self.parsed_arguments['width'] = match.groupdict()['width']
            return True

    def run(self):
        stdout = settings.DIRNAME + self.get_next_path()
        if not os.path.exists(self.stdout):
            cmd = 'convert -resize %s %s %s' % (self.parsed_arguments['width'], 
                                                settings.DIRNAME + self.stdin, 
                                                stdout) 
            p1 = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE, 
                                  stdin=subprocess.PIPE)
            (stdout_data, stderr_data) = p1.communicate(input=self.stdin)
        self.stdout = stdout


if __name__ == '__main__':
    filters = {}

    for filter_ in AAFilter.__subclasses__():
        filters[filter_.name] = filter_

    stdin = AAFilter.uri_to_path("file:///tmp/gourfinck_numer_04-S-Rcd.jpg")
    pipeline = "bw|embed"

    for command in [x.strip() for x in pipeline.split("|")]:
        if ":" in command:
            (filter_, arguments) = command.split(":", 1)
            filter_.strip()
            command.strip()
        else:
            (filter_, arguments) = (command.strip(), None)
        try:
            stdin = filters[filter_](arguments, stdin).run()
        except KeyError:
            stdin = """The "%s" filter doesn't exist""" % filter_
            break
    
    print(stdin)

#!/usr/bin/env python
#-*- coding:utf-8 -*-

import re, urlparse
from models import *
from aacore.settings import DEFAULT_REL_NAMESPACE

class LinkForm:
    """
    regex based parsing of mediawiki style links,

    ie of the form:
    [[ rel :: target # fragment | label ]]
    examples:
    [[ foo ]] (target: foo)
    [[ duration:: 03:45:23 ]] (rel: duration, target: 03:45:23)
    [[ homepage:: http://stdin.fr ]] (rel: homepage, target: http://stdin.fr)

    """

    #        (?:(?P<namespace>[^\]#]+?) \s* :)? \s*
    # [[ rel :: namespace : target # fragment | label ]]
    pat = re.compile(r"""\[\[ \s*
        (?P<contents>
            (?:(?P<rel>[^\]#]+?) \s* ::)? \s*
            (?P<target>[^\]#]+?)\s*
            (?:\# \s* (?P<fragment>[^\]]+?) )? \s*
            (?:\| \s* (?P<label>[^\]]+?) \s*)?
        ) \s*
    \]\]""", re.X)

    #    (?P<namespace> \s* (?P<namespace_name> [^\]#]+? ) \s* :)?
    # White space-preserving pattern
    ppat = re.compile(r"""\[\[
        (?P<rel> \s* (?P<rel_name> [^\]#]+? ) \s* ::)?
        (?P<target> \s* (?P<target_name> [^\]#]+? ) \s* )
        (?P<fragment> \# (?P<fragment_name> [^\]]+? ) \s* )?
        (?P<label> \| \s* (?P<label_name> [^\]]+? ) \s*)?
    \]\]""", re.X)

    # (?:#\s*(?P<fragment>[^\]]+?))?
    def __init__(self, match):
        self.source = match.group(0)
        d = match.groupdict()
        # HACK! CHECK IF ORIGINAL looks like a URL (http only at the moment!)
        contents = d['contents']
        urlparts = urlparse.urlparse(contents)
        if urlparts:
            scheme = urlparts[0]
            if scheme.lower() == "http" or scheme.lower() == "https":
                self.rel = None
                self.target = contents
                self.fragment = None
                self.label = None
                try:
                    hashpos = contents.rindex("#")
                    self.target = contents[:hashpos]
                    self.fragment = contents[hashpos + 1:]
                except ValueError:
                    pass
                return

        self.rel = d['rel']
        self.target = d['target']
        self.fragment = d['fragment']
        self.label = d['label']

# NEED TO;
# (1) RESOLVE REL (namespace:name)
# (2) LOOKUP THE REL TO GET ITS RELTYPE AND CODE ACCORDINGLY

def render_html (match):
    """ Render the link in HTML """

    link = LinkForm(match)
    label = link.label or link.target
    rel = link.rel or ""
    target = link.target

    if rel:
        if ":" not in rel:
            rel = DEFAULT_REL_NAMESPACE + ":" + rel
        (ns, rel) = rel.split(":", 1)
        ns = RelationshipNamespace.objects.get(name=ns)
        rel = ns.url + rel
        (rel, created) = Relationship.objects.get_or_create(url=rel)
        
        if rel._type == "uri":
            return """<a href="%s" rel="%s">%s</a>""" % (target, rel.compacturl, label)
        elif rel._type == "page":
            target = reverse("aacore.views.page", args=[wikify(target)])
            return """<a href="%s" rel="%s">%s</a>""" % (target, rel.compacturl, label)
        else:
            return """<span property="%s" content="%s">%s</span>""" % (rel.compacturl, target, label)
    else:
        if not target.startswith("http"):
            target = reverse("aacore.views.page", args=[wikify(target)])
        return """<a href="%s">%s</a>""" % (target, label)
        
#    if not item.startswith("http://"):
#        if namespace == "page" or namespace=="pages":
#            item = reverse("sarmawiki.views.page", args=[wikify(item)])
#        elif namespace == "tag" or namespace == "tags":
#            item = reverse("sarmawiki.views.tag", args=[wikify(item)])
#        elif namespace == "doc" or namespace=="docs":
#            try:
#                doc = Document.objects.get(pk=int(item))
#                label = link.label or doc.title
#                item = reverse("sarmadocs.views.doc", args=[doc.id])
#            except Document.DoesNotExist:
#                item = "#"
#                label = "Document %s not found!" % item

def markup(text):
    """ translate text to a list of Link objects """
    return LinkForm.pat.sub(render_html, text)

if __name__ == "__main__":
    import sys, codecs
    try:
        fin = sys.argv[1]
        fin = codecs.open(fin, "r", "utf-8")
    except IndexError:
        fin = sys.stdin
    sys.stdout.write(markup(fin.read()))


from django.template.defaultfilters import stringfilter
from django import template

import aacore.models


register = template.Library()


RELATIONSHIPS = None

@register.filter
def rel_name (url):
    url = unicode(url)
    ret = url    
    global RELATIONSHIPS
    if RELATIONSHIPS == None:
        RELATIONSHIPS = {}
        for rel in aacore.models.Relationship.objects.all():
            RELATIONSHIPS[rel.url] = rel
    rel = RELATIONSHIPS.get(url)
    if rel:
        ret = rel.name
        if not ret:
            (_, ret) = os.path.split(urlparse.urlparse(rel.url).path)
    
    return ret


@register.filter
@stringfilter
def compactnamespace (url):
    for ns in aacore.models.RelationshipNamespace.objects.all():
        if url.startswith(ns.url):
            return ns.name + ":" + url[len(ns.url):]
    return url


class AaAllPages(template.Node):
    def render(self, context):
        pages = aacore.models.Page.objects.all()
        print(pages)
        return pages


def aa_all_pages(parser, token):
    try:
        tag_name  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly 1 arguments" % token.contents.split()[0])
    return AaAllPages()
register.tag(aa_all_pages)

def page_list():
    return {
        'page_list': aacore.models.Page.objects.all(),
    }
register.inclusion_tag('aacore/partials/page_list.html')(page_list)


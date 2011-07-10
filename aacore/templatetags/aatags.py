import aacore.models
from django.template.defaultfilters import stringfilter
from django import template
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


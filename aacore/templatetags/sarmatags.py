from django.template.defaultfilters import stringfilter
from django import template

import aacore.models


register = template.Library()

def sidebar():
    """
    Returns an unordered list of all the wiki pages
    Usage:
        {% page_list %}
    """
    try:
        sidebar = aacore.models.Page.objects.get(name="Sidebar")
    except aacore.models.Page.DoesNotExist:
        sidebar = None
    return {
        'sidebar': sidebar
    }
register.inclusion_tag('aacore/partials/sidebar.html')(sidebar)

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

import django
from models import *
from utils import *

# from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, Http404, HttpResponseForbidden, HttpResponseNotAllowed

def page_list(request):
    """ A listing of All Pages (like MediaWiki Special:AllPages) """
    context = {}
    return django.shortcuts.render_to_response("aa_page_list.html", context, context_instance = django.template.RequestContext(request))

def page_detail (request, slug):
    """ Main view of a page """
    context = {}
    name = dewikify(slug)
    page = django.shortcuts.get_object_or_404(Page, name=name)
    return django.shortcuts.render_to_response("aa_page.html", context, context_instance = django.template.RequestContext(request))

import sniffer

def sniff (request):
    """
    Main URL sniffer view, collects all annotations from the sniffer plugins and displays them in a single page.
    Options: 'url' parameter
    Sniffing only displays information, it should not alter the database / create new resources
    """
    context = {}
    url = request.REQUEST.get('url', '')
    if url:
        data, annotations = sniffer.sniff(url)
        context['original_url'] = url
        context['data'] = data
        context['annotations'] = annotations    
        context['url'] = data.url
    return django.shortcuts.render_to_response("aa_sniff.html", context, context_instance = django.template.RequestContext(request))




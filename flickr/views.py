from django.shortcuts import (render_to_response, redirect, get_object_or_404)
from django.http import (HttpResponse, HttpResponseRedirect)
from django.template import (RequestContext, Template, Context)
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.conf import settings as projsettings
from django.contrib.auth.decorators import login_required

from models import *
from aacore.models import Namespace

def photo (request, id):
    context = {}
    photo = get_object_or_404(Photo, pk=id)
    context['about_url'] = photo.page_url
    context['photo'] = photo
    context['namespaces'] = Namespace.objects.all()
    exif = request.REQUEST.get("exif", "")
    if exif:
        context['exif'] = photo.get_exif()

    # url = reverse('aa-page-edit', kwargs={'slug': slug})
    return render_to_response("flickr/photo.html", context, context_instance=RequestContext(request))


from django.shortcuts import (render_to_response, redirect, get_object_or_404)
from django.http import (HttpResponse, HttpResponseRedirect)
from django.template import (RequestContext, Template, Context)
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.conf import settings as projsettings
from django.contrib.auth.decorators import login_required

from models import *
from aacore.models import Namespace


def media (request, id):
    context = {}
    asset = get_object_or_404(Media, pk=id)
    context['asset'] = asset
    context['namespaces'] = Namespace.objects.all()

    # url = reverse('aa-page-edit', kwargs={'slug': slug})
    return render_to_response("ffmpeg/media.html", context, context_instance=RequestContext(request))


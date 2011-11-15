from django.shortcuts import (render_to_response, redirect, get_object_or_404)
from django.http import (HttpResponse, HttpResponseRedirect)
from django.template import (RequestContext, Template, Context)
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.conf import settings as projsettings
from django.contrib.auth.decorators import login_required

from models import *
from aacore.models import Namespace

def video (request, id):
    context = {}
    video = get_object_or_404(Video, pk=id)
    context['video'] = video
    context['namespaces'] = Namespace.objects.all()

    # url = reverse('aa-page-edit', kwargs={'slug': slug})
    return render_to_response("youtube/video.html", context, context_instance=RequestContext(request))

def video_embed (request, id):
    context = {}
    video = get_object_or_404(Video, pk=id)
    context['video'] = video
    context['namespaces'] = Namespace.objects.all()
    return render_to_response("youtube/video_embed.html", context, context_instance=RequestContext(request))


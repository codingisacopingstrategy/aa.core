from django.shortcuts import (render_to_response, redirect, get_object_or_404)
from django.http import (HttpResponse, HttpResponseRedirect)
from django.template import (RequestContext, Template, Context)
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.conf import settings as projsettings
from django.contrib.auth.decorators import login_required

from models import *
from aacore.models import Namespace

def asset (request, id):
    context = {}
    asset = get_object_or_404(Asset, pk=id)
    context['asset'] = asset
    context['namespaces'] = Namespace.objects.all()

    # organize files by originals -> [derivs]
    files = []
    originalsByName = {}
    for f in asset.files.filter(source="original").order_by("filename"):
        t = (f, [])
        originalsByName[f.filename.strip("/")] = t
        files.append(t)
    missing = None
    for f in asset.files.exclude(source="original").order_by("filename"):
        try:
            ot = originalsByName[f.original.strip("/")]
        except KeyError:
            if missing == None:
                missing = ({"format": "MISSING ORIGINAL"}, [])
                files.append(missing)
            ot = missing
        ot[1].append(f)
            
    context['files'] = files

    # url = reverse('aa-page-edit', kwargs={'slug': slug})
    return render_to_response("internetarchive/asset.html", context, context_instance=RequestContext(request))


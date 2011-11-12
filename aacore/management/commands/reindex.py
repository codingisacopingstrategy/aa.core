from optparse import make_option
import RDF

from django.core.management.base import BaseCommand, CommandError
from aacore.settings import INDEXED_MODELS
import aacore.rdfutils #import rdf_parse_into_model
import aacore.utils # import full_site_url, get_rdf_model
import aacore.models # import Resource, ResourceDelegate


def ensure_resource_for_delegate(delegate):
    # REVERSE SYNC RESOURCE
    try:
        about_url = aacore.utils.full_site_url(delegate.get_about_url())
    except AttributeError:
        about_url = aacore.utils.full_site_url(delegate.get_absolute_url())

    res, created = aacore.models.Resource.objects.get_or_create(url=about_url)
    # check if link exists
    linkExists = False
    for o2 in res.delegates.all():
        if o2 == delegate:
            linkExists = True

    if not linkExists:
        dlink = aacore.models.ResourceDelegate(resource=res, delegate=delegate)
        dlink.save()

    return res

class Command(BaseCommand):
    args = ''
    help = ''
#    option_list = BaseCommand.option_list + (
#        make_option('--all',
#            action='store_true',
#            dest='all',
#            default=False,
#            help='Reindex all'),
#        )

    def handle(self, *args, **options):
        rdfmodel = aacore.utils.get_rdf_model()
        modelnames = args or INDEXED_MODELS
        errors = []
        for modelname in modelnames:
            try:
                (modulename, classname) = modelname.rsplit(".", 1)
                module = __import__(modulename, fromlist=[classname])
                klass = getattr(module, classname)
                for delegate in klass.objects.all():
                    ensure_resource_for_delegate(delegate)
                    delegate_url = aacore.utils.full_site_url(delegate.get_absolute_url())
                    print delegate_url
                    try:
                        aacore.rdfutils.rdf_parse_into_model(rdfmodel, delegate_url, format="rdfa", baseuri=delegate_url, context=delegate_url)
                    except RDF.RedlandError, e:
                        print "RDF ERROR"
                        errors.append(delegate_url)
            except ImportError:
                print "ERROR IMPORTING", modelname

        if errors:
            print "RDF errors occurred in the following:"
            for url in errors:
                print "\t", url


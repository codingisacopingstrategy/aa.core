from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from aacore.rdfutils import *
from aacore.utils import get_rdf_model, full_site_url, pagename_for_url
from aacore.models import Page

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
        model = get_rdf_model()
        samplepageurl = full_site_url(Page.objects.all()[0].get_absolute_url())
        samplepageurl = samplepageurl.rstrip("/")
        basepageurl = samplepageurl[:samplepageurl.rindex('/')] + "/"

        pagenames = {}
        Page.objects.all()
        for s in model:
            obj = s.object
            if obj.is_resource():
                url = unicode(obj.uri)
                if url.startswith(basepageurl):
                    pagenames[pagename_for_url(url)] = True
        for name in pagenames:
            (page, created) = Page.objects.get_or_create(name=name)
            if created:
                print "CREATED", name
        ## DROP ORPHAN PAGES
        for page in Page.objects.all():
            if page.name not in pagenames:
                if page.content.strip():
                    hastext = True
                else:
                    hastext = False
                print "ORPHAN PAGE", page.name, hastext
                if not hastext:
                    page.delete()
#        keys = pages.keys()
#        keys.sort()
#        for name in keys:
#            print name


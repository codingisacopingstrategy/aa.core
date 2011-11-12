from optparse import make_option
import urllib, urllib2
from django.core.management.base import BaseCommand, CommandError
from flickr.models import *


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-l', '--license',
            action='store',
            type='string',
            dest='license',
            help='License ID to optionally filter by, values: 0:Copyright, 1:CC-BY-NC-SA, 2:CC-BY-NC, 3:BY-NC-ND, 4:CC-BY, 5:CC-BY-SA, 6:CC-BY-ND, 7:Public domain, 8:US Gov'),
        make_option('-s', '--sort',
            action='store', 
            type='string',
            dest='sort',
            default="relevance",
            help='Values: date-posted-asc, date-posted-desc, date-taken-asc, date-taken-desc, interestingness-desc, interestingness-asc, and relevance (default)'),
        make_option('-n', '--perpage',
            action='store',
            type='int',
            default=20,
            dest='perpage',
            help='Limit number of returned results'),
    )
#    args = '\"searchterm\" limit'
#    help = 'Imports Photo results from search (if new)'

    def handle(self, *args, **options):
        search = args[0]
        j = api(method='flickr.photos.search', text=search, per_page=options.get("perpage"), sort=options.get("sort"), license=options.get("license"))
        for p in j['photos']['photo']:
            (photo, created) = Photo.objects.get_or_create(flickrid=p['id'])
            if created:
                print 'flickr:'+p['id']
                photo.load_info()


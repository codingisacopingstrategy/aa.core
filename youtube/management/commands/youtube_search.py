from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
# import gdata.youtube.service
from youtube.models import *


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-l', '--license',
            action='store',
            type='string',
            dest='license',
            help='Filter on license, possible values are "cc" for Creative Commons, and "youtube" (default)'),
        make_option('-o', '--orderby',
            action='store',
            type='string',
            dest='orderby',
            help='Values: relevance (default), published (reverse chrono), viewCount (most viewed), rating (highest rating)'),
        make_option('-m', '--maxresults',
            action='store',
            type='int',
            default=10,
            dest='maxresults',
            help='Limit number of returned results'),
    )

#    args = '\"searchterm\" orderby limit'
#    help = 'Imports YouTube video results from search (if new), orderby: (published, viewCount, relevance, rating)'

    def handle(self, *args, **options):
        search = args[0]
        try:
            limit = int(args[2])
        except IndexError:
            limit = 10

        feed = api(q=search, license=options.get("license"), orderby=options.get("orderby"), max_results=options.get("maxresults"))
        for entry in feed.xpath("//atom:entry", namespaces=NS):
            ytid = scalar(entry.xpath(".//yt:videoid/text()", namespaces=NS), default="")
            video, created = Video.objects.get_or_create(youtubeid=ytid)
            if created:
                print "youtube:"+ytid
                video.syncEntry(entry)



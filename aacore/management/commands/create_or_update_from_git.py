import codecs
import glob
import os
from django.core.management.base import BaseCommand, CommandError


from aacore.models import Page
from aacore import settings


class Command(BaseCommand):
    args = ''
    help = 'Synchronizes the database with the git repository.'

    def handle(self, *args, **options):
        for filename in glob.glob(os.path.join(settings.GIT_DIR, '*')):
            if not os.path.isdir(filename):
                basename = os.path.basename(filename)
                (page, did_exist) = Page.objects.get_or_create(name=basename)
                f = codecs.open(filename, 'r', 'utf-8')
                page.content = f.read()
                print("importing %s" % page.name)
                f.close()
                page.save()

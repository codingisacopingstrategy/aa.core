from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from ffmpeg.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        for arg in args:
            obj, created = Media.get_or_create_from_url(arg)
            if not created:
                obj.load_info()



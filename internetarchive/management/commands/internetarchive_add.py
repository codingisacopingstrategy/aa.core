from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from internetarchive.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        for arg in args:
            obj, created = Asset.get_or_create_from_url(arg)
            if not created:
                obj.sync()



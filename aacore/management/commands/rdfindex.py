from django.core.management.base import BaseCommand, CommandError
import aacore.rdfutils

class Command(BaseCommand):
    args = '<url ...>'
    help = 'url(s) to index'

    def handle(self, *args, **options):
        for arg in args:
            aacore.rdfutils.put_url(arg)

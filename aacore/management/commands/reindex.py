import RDF

from django.core.management.base import BaseCommand
import aacore.models
import aacore.utils
from aacore import get_indexed_models 
import aacore.signals


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
        if args:
            models = []
            for modelname in args:
                (modulename, classname) = modelname.rsplit(".", 1)
                module = __import__(modulename, fromlist=[classname])
                klass = getattr(module, classname)
                models.append(klass)
        else:
            models = get_indexed_models()

        for model in models:
            print("Reindexing %s instances" % model)
            for item in model.objects.all():
                print item.get_absolute_url()
                try:
                    aacore.signals.indexing_reindex_item(item)
                except RDF.RedlandError, e:
                    print "\tERROR,", e
            print



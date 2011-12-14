from optparse import make_option
import RDF

from django.core.management.base import BaseCommand, CommandError
import aacore.models
import aacore.utils


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
        if args:
            models = []
            for modelname in args:
                (modulename, classname) = modelname.rsplit(".", 1)
                module = __import__(modulename, fromlist=[classname])
                klass = getattr(module, classname)
                models.append(klass)
        else:
                models = aacore.utils.get_indexed_models()

        for model in models:
            for item in model.objects.all():
                print item.get_absolute_url()
                try:
                    aacore.models.indexing_reindex_item(item)
                except RDF.RedlandError, e:
                    print "\tERROR,", e



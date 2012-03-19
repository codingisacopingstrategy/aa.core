from django.core.management.base import BaseCommand
from aacore.utils import add_resource

class Command(BaseCommand):
    """
    >>> foo = Command()
    >>> foo.handle('http://lemonde.fr/')
    """
    args = '<url ...>'
    help = 'url(s) to index'

    def handle(self, *args, **options):
        for arg in args:
            add_resource(arg)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

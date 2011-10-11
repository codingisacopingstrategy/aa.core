from django.conf import settings


EXIFTOOL = getattr(settings, 'AA_EXIFTOOL', 'exiftool')
FFMPEG = getattr(settings, 'AA_FFMPEG', 'ffmpeg')
IDENTIFY = getattr(settings, 'AA_IDENTIFY', 'identify')
CONVERT = getattr(settings, 'AA_CONVERT', 'convert')

USER_AGENT = getattr(settings, 'AA_USER_AGENT', "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1) Gecko/20090624 Firefox/3.5")

DEFAULT_REL_NAMESPACE = getattr(settings, 'AA_DEFAULT_REL_NAMESPACE', "aa")
RDF_STORAGE_NAME = getattr(settings, 'AA_RDF_STORAGE_NAME', "aa")
RDF_STORAGE_DIR = getattr(settings, 'AA_RDF_STORAGE_DIR', ".")

GIT_DIR = getattr(settings, 'AA_GIT_DIR', "/home/aleray/work/aa.new/aa.core/repositories")

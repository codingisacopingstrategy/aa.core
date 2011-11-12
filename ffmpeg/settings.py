from django.conf import settings

FFMPEG = getattr(settings, 'AA_FFMPEG', 'ffmpeg')


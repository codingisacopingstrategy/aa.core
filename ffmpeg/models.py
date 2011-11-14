from django.db import models
import utils
from aacore.models import reindex_request


class Media (models.Model):
    class Meta:
        verbose_name_plural = "media"

    @classmethod
    def sniff(cls, url, request=None):
        pass

    @classmethod
    def get_or_create_from_url(cls, url, request=None, reload=False):
        try:
            ret = cls.objects.get(url=url)
            if reload: ret.sync()
            return ret, False
        except cls.DoesNotExist:
            info = utils.ffmpeg_get_info(url)
            if info:
                ret = Media.objects.create(url=url)
                ret.sync(info=info)
                return ret, True
            return None, False

    url = models.URLField(verify_exists=False)
    content_length = models.IntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    bitrate = models.IntegerField(null=True, blank=True)

    video_info_raw = models.CharField(blank=True, max_length=255)
    video_codec = models.CharField(blank=True, max_length=255)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    framerate = models.FloatField(null=True, blank=True, help_text="framerate (fps)")
    
    audio_info_raw = models.CharField(blank=True, max_length=255)
    audio_codec = models.CharField(blank=True, max_length=255)
    audio_bits = models.IntegerField(null=True, blank=True, help_text = "sampling depth (in bits)")
    audio_sampling_rate = models.IntegerField(null=True, blank=True, help_text = "sample rate (in hertz)")
    audio_bitrate = models.IntegerField(null=True, blank=True, help_text = "audio bit rate (in kb/s)")
    audio_channels = models.IntegerField(null=True, blank=True, help_text = "channels (mono = 1, stereo = 2)")

    ## metadata fields
    artist = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    date = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    copyright = models.CharField(max_length=255, blank=True)
    license = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=255, blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ('aa-ffmpeg-media', (str(self.id), ))

    def get_about_url(self):
        """ this gets used to do reverse lookup to resource """
        return self.url

    def __unicode__(self):
        return self.url

    @property
    def audio_channels_display (self):
        if self.audio_channels:
            if self.audio_channels == 1:
                return "mono"
            elif self.audio_channels == 2:
                return "stereo"
            else:
                return "{0} channels".format(self.audio_channels)

    def sync(self, info=None):
        if info == None:
            info = utils.ffmpeg_get_info(self.url)
        
        self.duration = info.get("duration")

        self.video_info_raw = info.get("video", "")
        self.video_codec = info.get("video_codec", "")
        self.width = info.get("width")
        self.height = info.get("height")
        self.framerate = info.get("fps")

        self.audio_info_raw = info.get("audio", "")
        self.audio_codec = info.get("audio_codec", "")
        self.audio_bits = info.get("audio_bits")
        self.audio_sampling_rate = info.get("audio_sampling_rate")
        self.audio_bitrate = info.get("audio_bitrate")
        self.audio_channels = info.get("audio_channels")
        
        meta = info.get("meta", {})
        self.artist = meta.get("artist", "")
        self.title = meta.get("title", "")
        self.date = meta.get("date", "")
        self.location = meta.get("location", "")
        self.copyright = meta.get("copyright", "")
        self.license = meta.get("license", "")
        self.contact = meta.get("contact", "")

        self.save()
        # request reindex (via signal)
        reindex_request.send(sender=self.__class__, instance=self)


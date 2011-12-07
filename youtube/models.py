from django.db import models
import re, dateutil.parser
import urllib, urllib2
import lxml.etree
from aacore.models import reindex_request

NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'media': 'http://search.yahoo.com/mrss/',
    'openSearch': "http://a9.com/-/spec/opensearch/1.1/",
    'gd': "http://schemas.google.com/g/2005",
    'yt': "http://gdata.youtube.com/schemas/2007",
}

def scalar (t, default=None, type=None):
    """ Utility for xpath return vals that are lists or None """
    if t:
        if type:
            return type(t[0])
        else:
            return t[0]
    else:
        return default

def api (**keys):
    """ Returns a lxml.etree, url to override default URL """
    opts = {
        'v': 2,                 # Using version 2 of the API
    }
    if "url" in keys:
        baseurl = keys['url']
        del keys['url']
    else:
        baseurl = "http://gdata.youtube.com/feeds/api/videos"
    for key, value in keys.items():
        if value != None:
            key = key.replace("_", "-")
            opts[key] = value
    url = baseurl + '?' + urllib.urlencode(opts)
    # print "API", url
    return lxml.etree.parse(urllib2.urlopen(url))

class License (models.Model):
    url = models.URLField(blank=True, verify_exists=False)
    name = models.CharField(max_length=255)

    def admin_count (self):
        return self.videos.count()

    def __unicode__(self):
        return self.name

class User (models.Model):
    gdata_url = models.URLField(verify_exists=False)
    url = models.URLField(verify_exists=False, blank=True)
    related_url = models.URLField(verify_exists=False, blank=True)
    username = models.CharField(max_length=255, blank=True)
    firstName = models.CharField(max_length=255, blank=True)
    lastName = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    thumbnail_url = models.URLField(verify_exists=False, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=255, blank=True)
    hobbies = models.CharField(max_length=255, blank=True)
    hometown = models.CharField(max_length=255, blank=True)
    subscriber_count = models.PositiveIntegerField(null=True, blank=True)
    view_count = models.PositiveIntegerField(null=True, blank=True)
    total_upload_views = models.PositiveIntegerField(null=True, blank=True)

    def __unicode__ (self):
        return self.username

    def admin_video_count (self):
        return self.videos.count()

    def admin_thumbnail (self):
        if self.thumbnail_url:
            return '<img src="' + self.thumbnail_url + '" />'
    admin_thumbnail.allow_tags = True

    def load_data(self):
        entry = api(url=self.gdata_url)
        self.syncEntry(entry)
        return entry

    def syncEntry (self, entry):
        self.username = scalar(entry.xpath("//yt:username/text()", namespaces=NS), "")
        self.url = scalar(entry.xpath('//atom:link[@rel="alternate"]/@href', namespaces=NS), default="")
        self.related_url = scalar(entry.xpath('//atom:link[@rel="related"]/@href', namespaces=NS), default="")
        self.thumbnail_url = scalar(entry.xpath('//media:thumbnail/@url', namespaces=NS), default="")
        self.firstName = scalar(entry.xpath('//yt:firstName/text()', namespaces=NS), default="")
        self.lastName = scalar(entry.xpath('//yt:lastName/text()', namespaces=NS), default="")
        self.gender = scalar(entry.xpath('//yt:gender/text()', namespaces=NS), default="")
        self.location = scalar(entry.xpath('//yt:location/text()', namespaces=NS), default="")
        self.hobbies = scalar(entry.xpath('//yt:hobbies/text()', namespaces=NS), default="")
        self.age = scalar(entry.xpath('//yt:age/text()', namespaces=NS), type=int)
        self.subscriber_count = scalar(entry.xpath('//yt:statistics/@subscriberCount', namespaces=NS), type=int)
        self.view_count = scalar(entry.xpath('//yt:statistics/@viewCount', namespaces=NS), type=int)
        self.total_upload_views = scalar(entry.xpath('//yt:statistics/@totalUploadViews', namespaces=NS), type=int)
        self.save()

    def admin_video_count (self):
        return self.videos.count()

class Tag (models.Model):
    name = models.CharField(max_length=255)

    def admin_video_count (self):
        return self.videos.count()

    def __unicode__ (self):
        return self.name

    def get_full_url (self):
        return "http://www.youtube.com/results?search_query=%s&search=tag"%(urllib.quote(self.name))


youtubevid_pat = re.compile(r"""^http://(www\.)?youtube\.com/watch\?v=(?P<id>[^&]+)""", re.I)
#def getYouTubeEntry (url):
#    m = youtubevid_pat.match(url)
#    if m:
#        youtubeid = m.groupdict()['id']
#        yt_service = gentry.youtube.service.YouTubeService()
#        return (id, yt_service.GetYouTubeVideoEntry(video_id=youtubeid))

def url_to_youtubeid (url):
    m = youtubevid_pat.search(url)
    if m:
        return m.groupdict().get("id")

#def youtubeid_to_url (ytid):
#    pass


class Video (models.Model):
    @classmethod
    def get_or_create_from_url(cls, url, reload=False):
        yid = url_to_youtubeid(url)
        try:
            ret = cls.objects.get(youtubeid=yid)
            if reload: ret.sync()
            return ret, False
        except cls.DoesNotExist:
            pass        

        if yid:
            ret = Video.objects.create(youtubeid=yid)
            ret.sync()
            return ret, True
        return None, False

    youtubeid = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True)
    license = models.ForeignKey(License, null=True, blank=True, related_name="videos")
    published = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=255, blank=True)
    tags = models.CharField(max_length=255, blank=True)
    watch_url = models.CharField(max_length=255, blank=True)
    flash_player_url = models.CharField(max_length=255, blank=True)
    view_count = models.PositiveIntegerField(null=True, blank=True)
    aspectRatio = models.CharField(max_length=255, blank=True)
#    location = models.CharField(max_length=255, blank=True)
#    rating = models.CharField(max_length=255, blank=True)
#    rating_num_raters = 

    author = models.ForeignKey(User, null=True, blank=True, related_name="videos")
    tags = models.ManyToManyField(Tag, null=True, blank=True, related_name="videos")

    db_created = models.DateTimeField(auto_now_add = True)
    db_lastmodified = models.DateTimeField(auto_now = True)
    
    ########################
    ## AA methods
    ######################## (required)

    @models.permalink
    def get_absolute_url(self):
        return ('aa-youtube-video', (str(self.id),))

    def get_about_url(self):
        """ this gets used to do reverse lookup to resource """
        return "http://www.youtube.com/watch?v=" + self.youtubeid

    ######################## (optional)

    def wiki_reference(self):
        return "youtube:" + self.youtubeid

    ########################

    def __unicode__ (self):
        return "YouTube video: %s (%s)" % (self.title, self.youtubeid)

    def sync (self):
        feed = api(url="http://gdata.youtube.com/feeds/api/videos/" + self.youtubeid)
        entry = feed.xpath("//atom:entry", namespaces=NS)[0]
        self.syncEntry(entry)
        # request reindex (via signal)
        reindex_request.send(sender=self.__class__, instance=self)

    @property
    def thumbnail_url (self):
        try:
            return self.thumbnails.order_by("width", "time")[0].url
        except IndexError:
            return

    def big_thumbnail_url (self):
        try:
            return self.thumbnails.order_by("-width", "time")[0].url
        except IndexError:
            return

    def admin_thumbnail (self):
        return '<img src="' + self.thumbnail_url + '" />'
    admin_thumbnail.allow_tags = True

    def syncEntry (self, entry):
        """ entry is a youtube gentry "entry" object """
        
        # url = entry.find(".//atom:id", namespaces=NS).text
        # self.youtubeid = scalar(entry.xpath(".//yt:videoid/text()", namespaces=NS))
        try:
            self.published = scalar(entry.xpath(".//atom:published/text()", namespaces=NS), type=dateutil.parser.parse)
        except TypeError:
            pass
        self.title = scalar(entry.xpath(".//atom:title/text()", namespaces=NS), default="")
        self.duration = scalar(entry.xpath(".//yt:duration/@seconds", namespaces=NS), type=int)
        self.category = scalar(entry.xpath(".//media:category/@label", namespaces=NS), default="")
        self.description = scalar(entry.xpath(".//media:description/text()", namespaces=NS), default="")
        self.watch_url = scalar(entry.xpath(".//media:player/@url", namespaces=NS), default="")
        self.aspectRatio = scalar(entry.xpath(".//yt:aspectRatio/text()", namespaces=NS), default="")
        license = scalar(entry.xpath(".//media:license", namespaces=NS))
        if license != None:
            self.license, created = License.objects.get_or_create(url=license.get("href"), name=license.text)

        self.flash_player_url = scalar(entry.xpath('.//atom:content[@type="application/x-shockwave-flash"]/@src', namespaces=NS), default="")
        view_count = scalar(entry.xpath('.//yt:statistics/@viewCount', namespaces=NS))
        if view_count:
            self.view_count = int(view_count)

        author_url = scalar(entry.xpath('.//atom:author/atom:uri/text()', namespaces=NS))
        if author_url:
            author, created = User.objects.get_or_create(gdata_url=author_url)
            if created:
                author.load_data()
            self.author = author

        self.save()

        tags = scalar(entry.xpath(".//media:keywords/text()", namespaces=NS))
        tags = tags.split(",")
        tags = [x.strip() for x in tags if x.strip()]
        ## clear any existing...
        for tag in self.tags.all():
            self.tags.remove(tag)
        for tagname in tags:
            (tag, created) = Tag.objects.get_or_create(name=tagname)
            self.tags.add(tag)

        VideoThumbnail.objects.filter(video=self).delete()
        for dthumb in entry.xpath(".//media:thumbnail", namespaces=NS):
            thumb = VideoThumbnail()
            thumb.video = self
            thumb.url = dthumb.get("url")
            thumb.width = dthumb.get("width")
            thumb.height = dthumb.get("height")
            time = dthumb.get("time")
            if time:
                thumb.time = time
            thumb.name = dthumb.get("{http://gdata.youtube.com/schemas/2007}name")
            thumb.save()
            
        VideoAlternateFormat.objects.filter(video=self).delete()
        for alternate in entry.xpath(".//media:content", namespaces=NS):
            format = VideoAlternateFormat()
            format.video = self
            format.url = alternate.get("url")
            format.ftype = alternate.get("type")
            format.isdefault = (alternate.get('isDefault') == "true")
            format.duration = alternate.get("duration")
            format.expression = alternate.get("expression")
            format.format = alternate.get("{http://gdata.youtube.com/schemas/2007}format")
            format.save()
            
class VideoAlternateFormat (models.Model):
    video = models.ForeignKey(Video, related_name="formats")
    url = models.CharField(max_length=255)
    ftype = models.CharField(max_length=255, blank=True)
    isdefault = models.BooleanField()
    duration = models.FloatField(null=True)
    expression = models.CharField(max_length=255, blank=True)
    format = models.CharField(max_length=255, blank=True)

class VideoThumbnail (models.Model):
    video = models.ForeignKey(Video, related_name="thumbnails")
    url = models.CharField(max_length=255)
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    time = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)
    

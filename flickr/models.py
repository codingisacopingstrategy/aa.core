import urllib, urllib2, re
import datetime, dateutil.parser
try: import simplejson as json
except ImportError: import json

from django.db import models
from flickr.apikey import apikey


def api (**keys):
    opts = {
        'api_key': apikey,
        'format': 'json',
        'nojsoncallback': '1',
    }
    for key, value in keys.items():
        if value != None:
            opts[key] = value
    url = "http://api.flickr.com/services/rest/?" + urllib.urlencode(opts)
    return json.load(urllib2.urlopen(url))

#    opts['text'] = search
#    opts['per_page'] = limit
#    opts['method'] = 'flickr.photos.search'
#    opts['sort'] = 'relevance'

class License (models.Model):
    @classmethod
    def load_and_create_all (cls):
        data = api(method="flickr.photos.licenses.getInfo")
        for datum in data.get("licenses").get("license"):
            l, created = License.objects.get_or_create(flickrid = datum['id'], name= datum['name'], url=datum['url'])

    @classmethod
    def get_by_id (cls, id):
        try:
            return License.objects.get(flickrid=id)
        except License.DoesNotExist:
            cls.load_and_create_all()
            return License.objects.get(flickrid=id)

    # flickr.photos.licenses.getInfo
    flickrid = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True, verify_exists=False)

    def admin_count (self):
        return self.photos.count()

    def __unicode__(self):
        return self.name


class User (models.Model):
    flickrid = models.CharField(max_length=255)
    username = models.CharField(max_length=255, blank=True)
    realname = models.CharField(max_length=255, blank=True)
    path_alias = models.CharField(max_length=255, blank=True, help_text="The slug of the username, in some ways the 'real' username")
    location = models.CharField(max_length=255, blank=True)
    photos_url = models.URLField(verify_exists=False, blank=True)
    profile_url = models.URLField(verify_exists=False, blank=True)
    ispro = models.BooleanField(default=False)
    iconfarm = models.CharField(max_length=255, blank=True)
    iconserver = models.CharField(max_length=255, blank=True)
    photos_count = models.IntegerField(null=True, blank=True)
    photos_first_date_taken = models.DateTimeField(null=True, blank=True)

    def __unicode__ (self):
        return self.username

    def name (self):
        return self.username

    def sync (self):
        info = api(method="flickr.people.getInfo", user_id=self.flickrid)
        info = info.get("person")
        self.realname = info.get("realname", {}).get("_content", "")
        self.username = info.get("username", {}).get("_content", "")
        self.path_alias = info.get("path_alias")
        self.photos_url = info.get("photosurl", {}).get("_content", "")
        self.profile_url = info.get("profileurl", {}).get("_content", "")
        self.location = info.get("location", {}).get("_content", "")
        self.ispro = info.get("ispro", False)
        self.iconfarm = info.get("iconfarm", "")
        self.iconserver = info.get("iconserve", "")

        photos = info.get("photos")
        if photos:
            self.photos_count = photos.get("count").get("_content")
            try:
                date_taken = photos.get("firstdatetaken").get("_content")
                self.photos_first_date_taken = dateutil.parser.parse(date_taken)
            except ValueError:
                print "\t<!>ValueError, parsing", date_taken
        self.save()
        # return info

    def get_full_url (self):
        return self.profile_url

flickr_url_pat = re.compile(r"""^http://www.flickr.com/photos/(?P<username>\w+)/(?P<photoid>\d+)/?$""", re.I)

class Photo (models.Model):
    @classmethod
    def get_or_create_from_url(cls, url, reload=False):
        try:
            # SHOULD MAYBE CONVERT URL to id, then search on flickrid NOT page_url
            ret = cls.objects.get(page_url=url)
            if reload:
                ret.sync()
            return ret, False
        except cls.DoesNotExist:
            pass        
        # Should such an object exist?
        m = flickr_url_pat.search(url)
        if m:
            fid = m.groupdict().get("photoid")
            ret = Photo.objects.create(flickrid=fid)
            ret.sync()
            return ret, True
        return None, False

    flickrid = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    page_url = models.URLField(blank=True, verify_exists=False)
 
    # the necessary info to construct the image URLs
    server = models.CharField(max_length=255, blank=True)
    farm = models.CharField(max_length=255, blank=True)
    secret = models.CharField(max_length=255, blank=True)

    date_posted = models.DateTimeField(null=True, blank=True)
    date_taken = models.DateTimeField(null=True, blank=True)
    license = models.ForeignKey(License, null=True, blank=True, related_name="photos")
    owner = models.ForeignKey(User, null=True, blank=True, related_name="photos")
    # tags = models.ManyToManyField(Tag, null=True, blank=True, related_name="photos")

    db_created = models.DateTimeField(auto_now_add = True)
    db_lastmodified = models.DateTimeField(auto_now = True)

    ########################
    ## AA methods
    ######################## (required)

    @models.permalink
    def get_absolute_url(self):
        return ('aa-flickr-photo', (str(self.id), ))

    def get_about_url(self):
        """ this gets used to do reverse lookup to resource """
        return self.page_url

    ######################## (optional)

    def wiki_reference (self):
        return "flickr:" + self.flickrid

    ########################

    def __unicode__ (self):
        return "Flickr photo: %s (%s)" % (self.title, self.flickrid)

#    @property 
#    def mediatype (self):
#        return "image"

#    @property 
#    def mediatype_descriptive (self):
#        return "photo"

#    @property
#    def author (self):
#        return self.owner


    """s	small square 75x75
t	thumbnail, 100 on longest side
m	small, 240 on longest side
-	medium, 500 on longest side
z	medium 640, 640 on longest side
b	large, 1024 on longest side*
o	original image, either a jpg, gif or png, depending on source format"""

    def image_url (self, code="t"):
        return "http://farm%(farm)s.static.flickr.com/%(server)s/%(id)s_%(secret)s_%(code)s.jpg" % {
            'farm': self.farm,
            'server': self.server,
            'secret': self.secret,
            'id': self.flickrid,
            'code': code
        }
 
    @property 
    def original_url (self):
        return self.image_url(code='o')

    @property
    def thumbnail_url (self):
        return self.image_url(code='t')

    @property 
    def small_still_url (self):
        return self.image_url(code='m')

    @property 
    def medium_still_url (self):
        return self.image_url(code='z')

    def admin_thumbnail (self):
        return '<img src="' + self.image_url(code="t") + '" />'
    admin_thumbnail.allow_tags = True

    # FLICKR exif data is packaged as a list of dicts:
    #{'clean': {'_content': 'JPEG'},
    # 'label': 'Compression',
    # 'raw': {'_content': '6'},
    # 'tag': 259,
    # 'tagspace': 'TIFF',
    # 'tagspaceid': 1}

    def load_data(self):
        info = api(method="flickr.photos.getInfo", photo_id=self.flickrid)
        return info

    def sync (self, data=None, load_comments=False):
        if data == None:
            data = self.load_data()
        """ requires that flickrid is set"""
        info = data['photo']
        # self.flickrid = p['id']
        
        self.title = info['title']['_content']
        self.description = info['description']['_content']
        self.page_url = info['urls']['url'][0]['_content']
     
        self.farm = info['farm']
        self.server = info['server']
        self.secret = info['secret']

        self.license = License.get_by_id(info.get('license'))

        # DATES
        # <dates posted="1100897479" taken="2004-11-19 12:51:19" takengranularity="0" lastupdate="1093022469" />
        dates = info.get("dates")
        if dates:
            date_posted = dates.get('posted')
            if date_posted:
                self.date_posted = datetime.datetime.fromtimestamp(float(date_posted))
            date_taken = dates.get('taken')
            if date_taken:
                self.date_taken = dateutil.parser.parse(date_taken)

        # owner
        (owner, created) = User.objects.get_or_create(flickrid=info['owner']['nsid'])
        if created:
            owner.sync()
        self.owner = owner

        # tags
        for dtag in info['tags']['tag']:
            #{u'raw': u'Anne Teresa De Keersmaeker', u'machine_tag': 0, u'id': u'11775692-5612607247-11507498', u'_content': u'anneteresadekeersmaeker', u'author': u'11868505@N08'}
            # label = dtag['raw']
            tag, created = Tag.objects.get_or_create(slug=dtag['_content'])
            ptag, created = PhotoTag.objects.get_or_create(tag=tag, photo=self)
            ptag.raw = dtag.get("raw")
            ptag.save()

        if load_comments:
            numcomments = int(info['comments']['_content'])
            if numcomments:
                self.load_comments()

        self.save()

    def load_comments(self):
        comments = api(method='flickr.photos.comments.getList', photo_id=self.flickrid)
        for c in comments['comments']['comment']:
            comment = Comment(photo=self)
            comment.body = c['_content']
            comment.authorid = c['author']
            comment.authorname = c['authorname']
            comment.save()

    def get_sizes (self):
        data = api(method="flickr.photos.getSizes", photo_id=self.flickrid)
        data = data.get("sizes").get("size")
        return data

    def get_exif (self):
        data = api(method="flickr.photos.getExif", photo_id=self.flickrid, secret=self.secret)
        data = data.get("photo").get("exif")
        fdata = []
        for datum in data:
            content = datum.get("clean")
            if content:
                content = content.get("_content")
            else:
                content = datum.get("raw").get("_content")
            fdata.append(dict(content=content, tagspace=datum.get("tagspace"),
                label=datum.get("label")))
        return fdata


#class Exif (models.Model):
#    photo = models.ForeignKey(Photo, related_name="exif")
#    tag = models.CharField(max_length=255)
#    tagspace = models.CharField(max_length=255)
#    content = models.CharField(max_length=255)

#    def __unicode__(self):
#        return "%s: %s" % (self.tag, self.content)

class Tag (models.Model):
    slug = models.CharField(max_length=255)
    photos = models.ManyToManyField(Photo, through='PhotoTag', related_name="tags")

    def __unicode__ (self):
        return self.slug

    def get_full_url (self):
        return "http://www.flickr.com/photos/tags/" + self.slug

    def admin_count(self):
        return self.photos.count()

class PhotoTag (models.Model):
    """PhotoTag allows the "raw" form of a tag to be recorded, which may vary"""
    tag = models.ForeignKey(Tag, related_name="phototags")
    photo = models.ForeignKey(Photo, related_name="phototags")
    raw = models.CharField(max_length=255, blank=True)

class Comment (models.Model):
    photo = models.ForeignKey(Photo, related_name="comments")
    authorid = models.CharField(max_length=255)
    authorname = models.CharField(max_length=255)
    body = models.TextField(blank=True)
 
    def __unicode__ (self):
        return "Comment on %s" % self.photo.flickrid


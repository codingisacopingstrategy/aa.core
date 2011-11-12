import urllib, urllib2, re
import datetime, dateutil.parser
try: import simplejson as json
except ImportError: import json

from django.db import models
from settings import SYNC_REVIEWS


urlpat = re.compile(r"^http://www.archive.org/details/(?P<id>[^/]+)/?", re.I)

#class License (models.Model):
#    url = models.URLField(verify_exists=False)
##    name = models.CharField(max_length=255)
#    def __unicode__(self):
#        return self.url
#    def assets_count (self):
#        return self.assets.count()

class User (models.Model):
    username = models.CharField(max_length=255)

    def __unicode__(self):
        return self.username

    def assets_count (self):
        return self.assets.count()

    @property
    def url (self):
        return "http://www.archive.org/search.php?" + urllib.urlencode({"query": 'creator:"{0}"'.format(self.username)})

class Collection (models.Model):
    shortname = models.CharField(max_length=255)
    fullname = models.CharField(max_length=255, blank=True)
    manual_url = models.URLField(verify_exists=False, blank=True, help_text="Idiomatic URLs can be optionally entered manually")

    def __unicode__(self):
        return self.shortname

    @property
    def url(self):
        if self.manual_url:
            return self.manual_url
        else:
            return "http://www.archive.org/details/" + self.shortname

    @property
    def name(self):
        return self.fullname or self.shortname

    def assets_count (self):
        return self.assets.count()

class MediaType (models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    def assets_count (self):
        return self.assets.count()

class Subject (models.Model):
    name = models.CharField(max_length=255)

    @property
    def url (self):
        return "http://www.archive.org/search.php?" + urllib.urlencode({"query": 'subject:"{0}"'.format(self.name)})

    def __unicode__(self):
        return self.name

    def assets_count (self):
        return self.assets.count()

class Asset (models.Model):
    @classmethod
    def sniff(cls, url, request=None):
        pass

    @classmethod
    def get_or_create_from_url(cls, url, request=None, reload=False):
        try:
            ret = cls.objects.get(url=url)
            if reload:
                ret.sync()
            return ret, False
        except cls.DoesNotExist:
            m = urlpat.search(url)
            if m:
                id = m.groupdict().get("id")
                ret = cls.objects.create(archiveid = m.groupdict().get("id"), url = url)
                ret.sync()
                return ret, True
            return None, False

    url = models.URLField(verify_exists=False)
    archiveid = models.CharField(max_length=255)

    misc_image = models.URLField(verify_exists=False, blank=True, help_text="IA's URL of the asset's thumbnail")
    misc_header_image = models.URLField(verify_exists=False, blank=True, help_text="IA's URL of the collection thumbnail")

    server = models.CharField(max_length=255, blank=True)
    _dir = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    titles_other = models.TextField(blank=True)
    mediatype = models.CharField(max_length=255, blank=True)
    license = models.URLField(verify_exists=False, blank=True)
    licenses_other = models.TextField(blank=True)

#    creator = models.CharField(max_length=255, blank=True)
#    collection = models.CharField(max_length=255, blank=True)
#    subject = models.TextField(blank=True) # (comma-delimted list)

    description = models.TextField(blank=True)
    descriptions_other = models.TextField(blank=True)

    date = models.DateTimeField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)

    publicdate = models.DateTimeField(null=True, blank=True)
    addeddate = models.DateTimeField(null=True, blank=True)
    # taper
    source = models.CharField(max_length=255, blank=True)
    runtime = models.CharField(max_length=255, blank=True) # (66:36)
    notes = models.TextField(blank=True)

    # item.downloads
    item_downloads = models.IntegerField(null=True, blank=True)
    reviews_num_reviews = models.IntegerField(null=True, blank=True)
    reviews_avg_rating = models.FloatField(null=True, blank=True)

#    licenses = models.ManyToManyField(License, null=True, blank=True, related_name="assets")
    creators = models.ManyToManyField(User, null=True, blank=True, related_name="assets")
    mediatypes = models.ManyToManyField(MediaType, null=True, blank=True, related_name="assets")
    collections = models.ManyToManyField(Collection, null=True, blank=True, related_name="assets")
    subjects = models.ManyToManyField(Subject, null=True, blank=True, related_name="assets")

    def __unicode__(self):
        return self.url

    @models.permalink
    def get_absolute_url(self):
        return ('aa-internetarchive-asset', (str(self.id), ))

    def wiki_reference (self):
        return 'ia:' + self.archiveid

    def get_data (self):
        return json.load(urllib2.urlopen(self.url + "?output=json"))

    def files_count (self):
        return self.files.count()

    def sync (self, data=None):
        if data == None:
            data = self.get_data()
        self.server = data.get("server", "")
        self._dir = data.get("dir", "")
        mdata = data.get("metadata")
        if mdata:
            titles = mdata.get("title", [])
            self.title = titles[0]
            self.titles_other = "\n".join(titles[1:])
            self.mediatype = ", ".join(mdata.get("mediatype", []))

            descriptions = mdata.get("description", [])
            self.description = descriptions[0]
            self.descriptions_other = "\n---\n".join(descriptions[1:])

            licenses = mdata.get("licenseurl", [])
            if len(licenses): self.license = licenses[0]
            self.licenses_other = "\n".join(licenses[1:])

            try:
                self.date = dateutil.parser.parse(mdata.get("date")[0])
            except TypeError:
                pass

            try:            
                self.year = int(mdata.get("year")[0])
            except TypeError:
                pass

            try:
                self.publicdate = dateutil.parser.parse(mdata.get("publicdate")[0])
            except TypeError:
                pass

            try:
                self.addeddate = dateutil.parser.parse(mdata.get("addeddate")[0])
            except TypeError:
                pass

            self.source = mdata.get("source", "")
            self.runtime = mdata.get("runtime", "")
            self.notes = mdata.get("notes", "")

#            self.creator = mdata.get("creator", "")
#            self.collection = mdata.get("collection", "")
#            self.subject = mdata.get("subject", "")

        misc = data.get("misc", {})
        self.misc_image = misc.get("image", "")
        self.misc_header_image = misc.get("header_image", "")

        item = data.get("item")
        if item:
            downloads = item.get("downloads", "")
            if downloads:
                self.downloads = int(downloads)

        self.save()

#        self.licenses.all().delete()
#        for n in mdata.get("licenseurl", []):
#            c, created = License.objects.get_or_create(url=n)
#            self.licenses.add(c)

        self.creators.all().delete()
        for n in mdata.get("creator", []):
            c, created = User.objects.get_or_create(username=n)
            self.creators.add(c)

        self.collections.all().delete()
        names = mdata.get("collection", [])
        for n in names:
            c, created = Collection.objects.get_or_create(shortname=n)
            self.collections.add(c)
            if (len(names) == 1) and (not c.fullname):
                c.fullname = misc.get("collection-title", "")
                c.save()

        self.mediatypes.all().delete()
        for n in mdata.get("mediatype", []):
            c, created = MediaType.objects.get_or_create(name=n)
            self.mediatypes.add(c)

        self.subjects.all().delete()
        for subjects in mdata.get("subject", []):
            for n in [x.strip() for x in subjects.split(";")]:
                c, created = Subject.objects.get_or_create(name=n)
                self.subjects.add(c)
        
        files = data.get("files")
        fileobjects = []
        if files:
            for filename, fdata in files.items():
                f, created = File.objects.get_or_create(asset=self, filename=filename)
                f.sync(fdata)
                fileobjects.append(f)
        for f in fileobjects:
            f.resolve_references()
        
        reviews = data.get("reviews")
        if reviews:
            info = reviews.get("info")
            if info:
                self.reviews_num_reviews = int(info.get("num_reviews", "0"))
                self.reviews_avg_rating = float(info.get("avg_rating", "0"))

            if SYNC_REVIEWS:
                self.reviews.all().delete()
                for rdata in reviews.get("reviews"):
                    rid = rdata.get("review_id")
                    r = Review.objects.create(asset=self)
                    r.sync(rdata)

        self.save()

    def files_list (self):
        """ Generate the nested listing of files and their derivatives """
        def subitems(f, level=1):
            ret = ""
            oname = f.filename.strip("/")
            subs = self.files.filter(original=oname).order_by("filename")
            if subs.count():
                ret += ("  "*level)+'<ul about="{}">\n'.format(f.url)
                for sub in subs:
                    ret += ("  "*(level+1))+'<li rev="dc:source"><span about="{1}"><span property="dc:format">{2}</span> <a href="{1}">{0}</a></span></li>\n'.format(sub.filename.strip("/"), sub.url, sub.format)
                    ret += subitems(sub, level+1)
                ret += ("  "*level)+"</ul>\n"
            return ret

        ret = "<ul>\n"
        for f in self.files.filter(source="original").order_by("filename"):
            ret += '  <li rev="dcterms:isPartOf"><span about="{1}"><span property="dc:format">{2}</span> <a href="{1}">{0}</a></span></li>\n'.format(f.filename.strip("/"), f.url, f.format)
            ret += subitems(f)
        ret += "</ul>\n"
        return ret

class File (models.Model):
    asset = models.ForeignKey(Asset, related_name="files")
    filename = models.CharField(max_length=255)
    format = models.CharField(max_length=255, blank=True)
    original = models.CharField(max_length=255, blank=True)
    original_file = models.ForeignKey('self', null=True, blank=True)
    md5 = models.CharField(max_length=255, blank=True)
    mtime = models.CharField(max_length=255, blank=True)
    size = models.CharField(max_length=255, blank=True)
    crc32 = models.CharField(max_length=255, blank=True)
    sha1 = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, blank=True)

    def sync(self, data):
        self.format = data.get("format", "")
        self.original = data.get("original", "")
        self.md5 = data.get("md5", "")
        self.mtime = data.get("mtime", "")
        self.size = data.get("size", "")
        self.crc32 = data.get("crc32", "")
        self.sha1 = data.get("sha1", "")
        self.source = data.get("source", "")
        self.save()

    def resolve_references (self):
        pass

    @property
    def url(self):
        return "http://" + self.asset.server + self.asset._dir + self.filename

class Review (models.Model):
    asset = models.ForeignKey(Asset, related_name="reviews")
    review_id = models.CharField(max_length=255, blank=True)
    reviewbody = models.TextField(blank=True)
    reviewtitle = models.CharField(max_length=255, blank=True)
    reviewer = models.CharField(max_length=255, blank=True)
    reviewdate = models.DateTimeField(null=True, blank=True)
    stars = models.CharField(max_length=255, blank=True)
    editedby = models.CharField(max_length=255, blank=True)

    def sync(self, data):
        self.review_id = data.get("review_id", "")
        self.reviewbody = data.get("reviewbody", "")
        self.reviewtitle = data.get("reviewtitle", "")
        self.reviewer = data.get("reviewer", "")
        self.reviewdate = dateutil.parser.parse(data.get("reviewdate", ""))
        self.stars = data.get("stars", "")
        self.editedby = data.get("editedby", "")
        self.save()



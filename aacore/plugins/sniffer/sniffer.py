from django.template import Context, loader

from aacore.resource_opener import ResourceOpener


def sniff (url):
    """
    Master sniffer: calls sniff method on all subclasses
    """
    data = ResourceOpener(url)
    data.get()
    info = {}
    info['content_type'] = data.content_type
    info['content_length'] = data.content_length
    info['charset'] = data.charset
    info['url'] = data.url
    info['original_url'] = data.original_url
    info['status'] = data.status
    info['filename'] = data.filename
    info['ext'] = data.ext
    info['etag'] = data.etag
    info['last_modified'] = data.last_modified
    info['last_modified_raw'] = data.last_modified_raw

    ret = []

    for subcls in Sniffer.__subclasses__():
        result = subcls().sniff(data.url, data.file, info)
        if result:
            ret.append(result)
    return data, ret

class Sniffer (object):
    """
    Base class of all "sniffer" objects
    """
    @classmethod
    def sniff (cls, url, reqfile, info):
        return None

class HttpSniffer (Sniffer):
    """ Annotation describing the contents of the http headers """
    @classmethod
    def sniff (cls, url, reqfile, info):
        t = loader.get_template('aacore/http_sniffer.html')
        c = Context(info)
        return t.render(c)


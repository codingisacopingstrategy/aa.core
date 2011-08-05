import html5lib, urllib2, lxml

from django.template.defaultfilters import stringfilter
from django import template
import urlparse

register = template.Library()


@register.filter
@stringfilter
def xpath (value, arg):
    """ Takes a url as input value and an xpath as argument.
    Returns a collection of html elements
    usage:
        {{ "http://fr.wikipedia.org/wiki/Antonio_Ferrara"|xpath:"//h2" }}
    """
    def absolutize_refs (baseurl, lxmlnode):
        for elt in lxml.cssselect.CSSSelector("*[src]")(lxmlnode):
            elt.set('src', urlparse.urljoin(baseurl, elt.get("src")))
        return lxmlnode
    request = urllib2.Request(value)
    request.add_header("User-Agent", "Mozilla/5.0 (X11; U; Linux x86_64; fr; rv:1.9.1.5) Gecko/20091109 Ubuntu/9.10 (karmic) Firefox/3.5.5")
    stdin = urllib2.urlopen(request)
    htmlparser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"), namespaceHTMLElements=False)
    page = htmlparser.parse(stdin)
    p = page.xpath(arg)
    if p:
        return "\n".join([lxml.etree.tostring(absolutize_refs(value, item), encoding='unicode') for item in p])
    else:
        return None
xpath.is_safe = True

@register.filter
@stringfilter
def embed (value, arg):
    """ Takes an audio/video ressource uri as input value and a player type as argument.
    returns html
    usage:
        {{ "http://video.constantvzw.org/AAworkshop/MVI_1675.ogv"|embed:"html5" }}
    """
    if arg is None or arg not in ['html5']:
        arg = html5
    if arg == "html5":
        return """<video width="320" height="240" controls="controls">
        <source src="%s" type="video/ogg" />
        Your browser does not support the video tag.
        </video>""" % value
    else:
        return None
embed.is_safe = True


#@register.filter
#def crop(uri, size='200w'):
    #""" Takes an image ressource uri as input value and a size as argument
    #returns the url of the new image
    #usage:
        #{{ http://mysite.org/myimage.png | crop }}
    #"""
    #SCALE_WIDTH = 'w'
    #SCALE_HEIGHT = 'h'
    #SCALE_BOTH = 'both'

    #def scale(max_x, pair):
        #x, y = pair
        #new_y = (float(max_x) / x) * y
        #return (int(max_x), int(new_y))

    ## defining the size
    #if (size.lower().endswith('h')):
        #mode = 'h'
        #size = size[:-1]
        #height = int(size.strip())
        #width = ""
    #elif (size.lower().endswith('w')):
        #mode = 'w'
        #size = size[:-1]
        #width = int(size.strip())
        #height = ""
    #else:
        #mode = 'both'
        #size = size.split("x")
        #width = int(size[0].strip())
        #height = int(size[1].strip())
        
    ## defining the filename and the miniature filename
    #filehead, filetail = os.path.split(file.path)
    #basename, format = os.path.splitext(filetail)
    #miniature = basename + '_thumb_' + str(width) + str(height) + format
    #filename = file.path
    #miniature_filename = os.path.join(filehead, miniature)
    #filehead, filetail = os.path.split(file.url)
    #miniature_url = filehead + '/' + miniature

    #if os.path.exists(miniature_filename) and os.path.getmtime(filename)>os.path.getmtime(miniature_filename):
        #os.unlink(miniature_filename)

    ## if the image wasn't already resized, resize it
    #if not os.path.exists(miniature_filename):
        
        ## See http://redskiesatnight.com/2005/04/06/sharpening-using-image-magick/
        ## for unsharpening values
        #if mode == SCALE_HEIGHT:
            #cmd = 'convert %s -resize x%d -unsharp 0.5x0.5+0.75+0.05     %s' % (filename, height, miniature_filename)
        #elif mode == SCALE_WIDTH:
            #cmd = 'convert %s -resize %d -unsharp 0.5x0.5+0.75+0.05 %s' % (filename, width, miniature_filename)
        #elif mode == SCALE_BOTH:
            #cmd = 'convert %s -resize %dx%d -unsharp 0.5x0.5+0.75+0.05 %s' % (filename, width, height, miniature_filename)
        #else:
            #raise Exception("Thumbnail size must be in ##w, ##h, or ##x## format.")
        
        #os.system(cmd)   

    #return miniature_url


@register.filter
@stringfilter
def zoom (value):
    """ Takes a url as input value and an xpath as argument.
    Returns a collection of html elements
    usage:
        {{ "http://upload.wikimedia.org/wikipedia/commons/c/cd/Tympanum_central_mosaic_santa_Maria_del_Fiore_Florence.jpg"|zoom }}
    """
    from django.template.loader import render_to_string
    rendered = render_to_string('aacore/partials/zoom.html', { 'value': value })
    return rendered
    
zoom.is_safe = True

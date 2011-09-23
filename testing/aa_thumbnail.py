#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Preview & thumbnail maker for images.

Requires: imagemagick

Sources:

Making Square Thumbnails with Imagemagick
http://www.randomsequence.com/articles/making-square-thumbnails-with-imagemagick/

"""

import os

command = """

    convert "{0[originalpath]}"\
        -resize {0[resize]}\>\
        "{0[previewpath]}"

    convert "{0[previewpath]}"\
        -thumbnail x200 -resize '200x<' -resize 50%\
        -gravity center -crop 100x100+0+0 +repage -format jpg -quality 91\
        "{0[thumbnailpath]}"

""".strip()

metadata = """

<div itemscope about="{0[originalpath]}" style="float: left"> 
    <a itemprop="preview" rel="aa:preview" href="{0[previewpath]}"><img itemprop="thumbnail" rel="aa:thumbnail" src="{0[thumbnailpath]}" /></a>
    <a rel="aa:thumbnail" href="{0[thumbnailpath]}"></a>
    <a itemprop="original" href="{0[originalpath]}"></a>
</div>

""".strip()


def do (**args):
    """ force with prevent checking if paths already exist """
    force = args.get("force", False)
    docmd = force
    if not force:
        docmd = not os.path.exists(args.get("previewpath")) or not os.path.exists(args.get("thumbnailpath"))

    if docmd:
        os.system(command.format(args))
    return metadata.format(args)

if __name__ == "__main__":
    do(originalpath = sys.argv[1], resize="1024x768", previewpath = sys.argv[2], thumbnailpath=sys.argv[3])



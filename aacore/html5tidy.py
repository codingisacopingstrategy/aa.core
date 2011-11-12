#!/usr/bin/env python
#-*- coding:utf-8 -*-

import html5lib, lxml.etree


"""
Simple wrapper around html5lib & lxml.etree to "tidy" html in the wild to well-formed xml/html

usage: html5tidy [-h] [-f] [--inputencoding INPUTENCODING] [--inputnometa]
                 [--inputnochardet] [-m METHOD] [--prettyprint]
                 [--outputencoding OUTPUTENCODING] [--xmldeclaration]
                 [source]
"""
parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"), namespaceHTMLElements=False)

def tidy(src, fragment=False, container="div", encoding=None, parseMeta=True, useChardet=True, method="xml", pretty_print=False, xml_declaration=None, output_encoding="utf-8"):
    if fragment:
        parts = parser.parseFragment(src, container=container, encoding=encoding, parseMeta=parseMeta, useChardet=useChardet)
    else:
        parts = [parser.parse(src, encoding=encoding, parseMeta=parseMeta, useChardet=useChardet)]

    ret = ""
    for p in parts:
        t = type(p)
        if (t == str or t == unicode):
            ret += p
        else:
            ret += lxml.etree.tostring(p, method=method, pretty_print=pretty_print,\
                xml_declaration=xml_declaration, encoding=output_encoding)

    return ret

if __name__ == "__main__":
    import argparse, urllib2, sys, urlparse

    argparser = argparse.ArgumentParser(description='Tidy HTML input using html5lib (input) + lxml (output)')
    # input
    argparser.add_argument('source', nargs="?", default=None, help='path or URL to read, stdin if not given')
    argparser.add_argument('-f', '--fragment', action='store_true', help='parse as fragment (no header etc added)')
    argparser.add_argument('--inputencoding', default=None, help='force INPUTENCODING on input, default is meta/auto detection')
    argparser.add_argument('--inputnometa', dest="meta", action='store_false', help='do not parse the meta tag on input')
    argparser.add_argument('--inputnochardet', dest="chardet", action='store_false', help='do not attempt to auto detect character set on input')
    # output
    argparser.add_argument('-m', '--method', default='xml', help="'xml', 'html', plain 'text' (text content without tags) or 'c14n'. Default is 'xml'.")
    argparser.add_argument('--prettyprint', action='store_true', help="enables (minimally) formatted XML")
    argparser.add_argument('--outputencoding', default="utf-8", help="output encoding. Use ascii to force character entity escaping of non-ascii. Default is utf-8.")
    argparser.add_argument('--xmldeclaration', action='store_true', help="force xml declaration, (default is only if not utf-8/ascii)")

    args = argparser.parse_args()

    xml_declaration = None
    if args.xmldeclaration: xml_declaration = True

    if args.source:
        if urlparse.urlparse(args.source).scheme:
            f = urllib2.urlopen(args.source)
        else:
            f = open(args.source)

    else:
        f = sys.stdin

    sys.stdout.write(tidy(f,
        encoding=args.inputencoding,
        parseMeta=args.meta,
        useChardet=args.chardet,
        method=args.method,
        pretty_print=args.prettyprint,
        xml_declaration=xml_declaration,
        output_encoding=args.outputencoding
    ))



import sys
sys.path.append("/home/aleray/work/aa.new/aa.core")
import aacore.mdx as mdx


f = open(sys.argv[1], 'r')
src = f.read()
f.close()

md = mdx.get_markdown()
html = md.convert(src.decode('utf-8'))


import codecs
f = codecs.open(sys.argv[2], "w", "utf-8" )
f.write(html)
f.close()

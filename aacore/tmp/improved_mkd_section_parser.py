#!/usr/bin/env python



def parse(input_lines):
    # Track if the previous line or the line before that was a url.

    # This is a bit silly. We should perhaps just peek at lines
    # when we find a header instead of keeping track of this.
    prev_url = prev_prev_url = False

    # The contents of the to-be-emitted block: optional url, header
    # (None for data before the first block), content.
    url = None
    header = None
    lines = []

    for line in input_lines:
        # Check for an atx-style header (this check might need to be stricter).
        if line.startswith('#'):
            if prev_url:
                new_url = lines.pop()
            else:
                new_url = None

            # Emit the previous block:
            yield url, header, lines

            # Set up the next block:
            prev_url = prev_prev_url = False
            url = new_url
            header = line
            lines = []
            continue

        # Check for a settext-style block:
        if any(all(c == underline_c for c in line.strip())
                 for underline_c in '-='):
            # We found the underline, check if the previous line is a header:
            if lines and len(lines[-1].strip()) == len(line.strip()):
                # The previous line was the header. Pop it and the
                # possible url before emitting the previous block:
                new_header = lines.pop()
                if prev_prev_url:
                    new_url = lines.pop()
                else:
                    new_url = None

                yield url, header, lines

                # And set up the next block.
                prev_url = prev_prev_url = False
                url = new_url
                header = new_header
                lines = []
                continue

        prev_prev_url = prev_url
        # Check for a url (this check may have to be stricter).
        # This only matters if it is followed by a header.
        prev_url = line.startswith('http://')
        lines.append(line)

    yield url, header, lines



txt = """
http://blablablabla.com
# header
fdfddffdfd
fdfdfdfd
http://otherurl
# fdfdfdfdfd
dffdfdfdfdfd
## fdfdfdfdfdfdfd
fdsffdfd
dffdfdfd
http://spork
header
======
settext content
another header
==============
url-less settext content
# blabla
dfffd
"""

if __name__ == '__main__':
    for url, header, lines in parse(txt.split('\n')):
        if url is not None:
            print 'url:', url
        print 'header:', header
        print lines

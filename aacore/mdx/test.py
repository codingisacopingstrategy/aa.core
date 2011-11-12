test = """
# Test{@style=left: 250px; top: 100px;}

Hello world.

00:01:00 --> 00:02:17

This is a timed annotation

00:03:00 -->

At three minutes.
    """
    md = get_markdown()

    print md.convert(test)


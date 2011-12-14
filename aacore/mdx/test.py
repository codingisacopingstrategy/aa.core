
test = """
[[hello|Label]]
    """
md = get_markdown()
print md.convert(test)


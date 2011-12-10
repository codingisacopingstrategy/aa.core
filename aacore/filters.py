import subprocess
import os.path


# TODO: seperate in 2 subclasses: string filters and file filters? String
#       filters could also be cached as html snippets?


class AAFilter(object):
    myname = "template"
    def __init__(self, arguments, original, stdin, previous, rdf_model=None):
        self.arguments = arguments or ""
        self.original = original
        self.previous = previous or original
        self.rdf_model = rdf_model
        self.stdin = stdin
        self.next_ = None

    def get_next_path(self):
        extension = os.path.splitext('blabla/bla.jpg')[1]
        self.next_ = "%s|%s:%s%s" % (self.previous, self.__class__.__name__, 
                                       self.arguments, extension)
        return self.next_

    def run(self):
        return (self.get_next_path(), "stdout")


class AAFilterEmbed(AAFilter):
    name = "embed"
    def run(self):
        stdout = '<audio src="%s" />' % self.original
        return (self.get_next_path(), stdout)


class AAFilterBW(AAFilter):
    name = "bw"
    def run(self):
        cmd = 'convert -colorspace gray %s %s' % (self.previous, self.get_next_path())
        p1 = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE, 
                              stdin=subprocess.PIPE)
        (stdout, stderr) = p1.communicate(input=self.stdin)
        return (self.get_next_path(), stdout)


class AAFilterLower(AAFilter):
    name = "lower"
    def run(self):
        cmd = 'tr "[:upper:]" "[:lower:]"'
        p1 = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE, 
                              stdin=subprocess.PIPE)
        (stdout, stderr) = p1.communicate(input=self.stdin)
        return (self.get_next_path(), stdout)


class AAFilterUpper(AAFilter):
    name = "upper"
    def run(self):
        return (self.get_next_path(), "stdout")


if __name__ == '__main__':
    filters = {}

    for filter_ in AAFilter.__subclasses__():
        filters[filter_.name] = filter_

    pipeline = "lower | bw"

    filename = "/home/aleray/equipe.jpg"
    #filename = "/path/to/my/file.txt"
    current_path = None
    stdout = "dsqs lLIUH IH lih lih lihu"
    for command in [x.strip() for x in pipeline.split("|")]:
        if ":" in command:
            (filter_, arguments) = command.split(":", 1)
            filter_.strip()
            command.strip()
        else:
            (filter_, arguments) = (command.strip(), None)
        (current_path, stdout) = filters[filter_](arguments, filename, stdout, current_path).run()
        print(current_path, stdout)


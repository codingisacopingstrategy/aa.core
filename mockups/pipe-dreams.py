

RES001: {{ http://video.ogg }}
RES002: {{ http://video.ogg | extractaudio }}
RES003: {{ http://video.ogg | extractaudio | normalize }}


request RES03
if does not exist:
    creates RES03
    set RES03.STATE to pending
    RES03 checks if RES02 exists
    if does not exist:
        exit
        creates RES02
        ...
        RES02 created:
            callback to RES03

def create(p):
    (res, created) = Resource.objects.get_or_create(pipeline=p)
    # checks if there is a parent
    parts = p.split("|")
    parent_pipeline = "|".join(parts[:-1]).strip()
    if len(parent_pipeline):
        # recurses
        res.parent = create(parent_pipeline)
        res.save()
    return res

class Resource (models):
    pipeline = "... | ..."
    state = (*PENDING|READY)
    local_file = None|path/to/file
    previous = models.OneToOneField("self", related_name='next', null=True, blank=True)

    def task (self, triggering_object=None):
        do your thing...
        state = READY
        if self.next:
            self.next.task()
    


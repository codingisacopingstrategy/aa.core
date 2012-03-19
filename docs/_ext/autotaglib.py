"""
    Extension of Sphinx autodoc for Django template tag libraries.

    Usage:
       .. autotaglib:: some.module.templatetags.mod
           (options)

    Most of the `module` autodoc directive flags are supported by `autotaglib`.     

    Andrew "Hatter" Ponomarev, 2010
"""

from sphinx.ext.autodoc import ModuleDocumenter, members_option, members_set_option, bool_option, identity
from sphinx.util.inspect import safe_getattr

from django.template import get_library, InvalidTemplateLibrary

class TaglibDocumenter(ModuleDocumenter):           
    """
    Specialized Documenter subclass for Django taglibs.
    """
    objtype = 'taglib'
    directivetype = 'module'
    content_indent = u''

    option_spec = {
        'members': members_option, 'undoc-members': bool_option,
        'noindex': bool_option,
        'synopsis': identity,
        'platform': identity, 'deprecated': bool_option,
        'member-order': identity, 'exclude-members': members_set_option,
    }

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        # don't document submodules automatically
        return False

    def import_object(self):
        """
        Import the taglibrary.

        Returns True if successful, False if an error occurred.
        """
        # do an ordinary module import      
        if not super(ModuleDocumenter, self).import_object():
            return False        

        try:    
            # ask Django if specified module is a template tags library
            # and - if it is so - get and save Library instance         
            #self.taglib = get_library(self.object.__name__)
            self.taglib = get_library(self.object.__name__.split('.', -1))
            return True
        except InvalidTemplateLibrary, e:
            self.taglib = None
            self.directive.warn(unicode(e))

        return False    

    def get_object_members(self, want_all):
        """
        Decide what members of current object must be autodocumented.

        Return `(members_check_module, members)` where `members` is a
        list of `(membername, member)` pairs of the members of *self.object*.

        If *want_all* is True, return all members.  Else, only return those
        members given by *self.options.members* (which may also be none).
        """
        if want_all:
            return True, self.taglib.tags.items()
        else:
            memberlist = self.options.members or []
        ret = []
        for mname in memberlist:
            if mname in taglib.tags:
                ret.append((mname, self.taglib.tags[mname]))
            else:
                self.directive.warn(
                    'missing templatetag mentioned in :members: '
                    'module %s, templatetag %s' % (
                    safe_getattr(self.object, '__name__', '???'), mname))
        return False, ret

def setup(app):
    app.add_autodocumenter(TaglibDocumenter)

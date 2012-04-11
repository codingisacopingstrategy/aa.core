.. aacore documentation master file, created by
   sphinx-quickstart on Thu Mar 15 21:26:18 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to aacore's documentation!
==================================

Active Archives aacore is a python application for the Django framework
designed to index web resources (identified through their URI) using RDF.

Strategically, the project aims to clarify some of the "cloudy" aspects of Web
2.0 regarding issues of licensing, sharing, ownership, access, and longevity of
online material.

Aacore provides the following features:

- Index web resources in a (Redland) RDF store
- Sniff a resource metadata using delegates
- Dump a list of all the indexed resources
- Browse a resource metadata marked up with RDFa
- Execute SPARQL queries against the RDF store 

Active Archives aacore is the cornerstone of other django applications such as
aawiki, a wiki initially designed to work with video and audio web resources.
Aawiki inverts the paradigm of uploading resources into a centralized server
and instead allows resources to remain "active", in-place and online. Caching
and proxy functionality allow (light-weight) copies of resources to be
manipulated and preserved even as the original sources change or become
(temporarily) unavailable.

This is alpha software with known bugs. It runs, and works at least some of
the time, but use at your own risk.

For more information about the project, see http://activearchives.org/.

Contents:

.. toctree::
   :maxdepth: 2


Installation
============

This document provides convenient steps so a user/developer can have aacore
running quickly.


Dependencies
------------

Please first install these software in order to get aacore running properly:

  - Django += 1.3 (http://www.djangoproject.org/)
  - SQLite3 (http://www.sqlite.org/)
  - PySQLite2 (http://trac.edgewall.org/wiki/PySqlite)
  - Python librdf (Redland) (http://librdf.org/)
  - Python html5lib (http://code.google.com/p/html5lib/)
  - Python dateutil (http://labix.org/python-dateutil)
  - Python docutils (http://docutils.sourceforge.net/)
  - Python lxml (http://lxml.de/)

The prefered way to install the python dependencies is to set up a virtual
environment and use ``pip``. Unfortunatly, librdf isn't available on Pypi which
mean you'll have to install it using your distribution package manager.

On Ubuntu, this should do the trick:

.. code-block:: bash

     sudo apt-get install python-librdf
     sudo apt-get install virtualenv
     cd $AACORE_PATH
     virtualenv venv
     source venv/bin/activate
     pip install -r requirements.txt

Additionally, you'll need the following programs for the default RDF sniffers:

  - Exiftool
  - Ffmpeg
  - Imagemagick


Quick Installation
------------------

1. Clone the repository onto your machine

    .. code-block:: bash

           git clone git@git.constantvzw.org:aa.core.git 

2. Once you've installed the required dependencies:

    .. code-block:: bash

           cd /path/to/aa.core/run

3. Build the database:

    .. code-block:: bash

           python manage syncdb

   The prompt will ask for the admin infos and fixtures will be loaded.
   
4. Run the django webserver:

    .. code-block:: bash

           python manage.py runserver

5. Configure the project domain name at:

       http://localhost:8000/admin/sites/site/1/

   Typically the value must be "localhost:8000" if you are running the project
   on a local server.


Glossary
========

Resource
    Resource can be two things:

    1. an Internet resource, referenced by a URI
    2. a django object represention an Internet resource
    3. ...

Resource delegate
   Description to come.

RDF Delegate
   Description to come.

Namespace
   Description to come.

Model
   Description to come.

Store
   Description to come.


Indexing resources
==================

>>> from aacore.models import Resource
>>> url = "http://video.constantvzw.org/AAworkshop/saturdaytimelapse.ogv"
>>> (resource, created) = Resource.get_or_create_from_url(url)
>>> resource
<Resource: http://video.constantvzw.org/AAworkshop/saturdaytimelapse.ogv>
>>> created
True
>>> resource.content_type
u'video/ogg'
>>> resource.content_length
2288612



Delegates
=========

To be completed


API Reference
=============

aacore.settings
---------------

.. automodule:: aacore.settings
    :inherited-members:


aacore.models
-------------

.. automodule:: aacore.models
    :members:


aacore.views
------------

.. automodule:: aacore.views
    :members:

aacore.rdfviews
---------------
 
.. automodule:: aacore.rdfviews
    :members:

aacore.resource_opener
----------------------

.. automodule:: aacore.resource_opener
    :members:

aacore.utils
------------

.. automodule:: aacore.utils
    :members:

aacore.rdfutils
---------------

.. automodule:: aacore.rdfutils
    :members:


aacore.templatetags.aacoretags
------------------------------

.. autotaglib:: aacore.templatetags.aacoretags
   :members:
   :undoc-members:
   :noindex:
 
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


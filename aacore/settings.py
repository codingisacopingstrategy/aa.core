# This file is part of Active Archives.
# Copyright 2006-2011 the Active Archives contributors (see AUTHORS)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Also add information on how to contact you by electronic and paper mail.


from django.conf import settings
import os.path


EXIFTOOL = getattr(settings, 'AA_EXIFTOOL', 'exiftool')
FFMPEG = getattr(settings, 'AA_FFMPEG', 'ffmpeg')
IDENTIFY = getattr(settings, 'AA_IDENTIFY', 'identify')
CONVERT = getattr(settings, 'AA_CONVERT', 'convert')

USER_AGENT = getattr(settings, 'AA_USER_AGENT', "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1) Gecko/20090624 Firefox/3.5")

DEFAULT_REL_NAMESPACE = getattr(settings, 'AA_DEFAULT_REL_NAMESPACE', "aa")
RDF_STORAGE_NAME = getattr(settings, 'AA_RDF_STORAGE_NAME', "aa")

# FIXME: Change this setting to an absolute path as it throws a redland error
# on production
RDF_STORAGE_DIR = getattr(settings, 'AA_RDF_STORAGE_DIR', ".")

# List of models that are indexed by the RDF Store
INDEXED_MODELS = getattr(settings, 'AA_INDEXED_MODELS', ("aacore.models.Resource", "aacore.models.Page",))
RESOURCE_DELEGATES = getattr(settings, 'AA_RESOURCE_DELEGATES', ())

CACHE_DIR = getattr(settings, 'AA_CACHE_DIR', os.path.join(settings.MEDIA_ROOT, "cache"))
CACHE_URL = getattr(settings, 'AA_CACHE_URL', os.path.join(settings.MEDIA_URL, "cache"))
GIT_DIR = getattr(settings, 'AA_GIT_DIR', os.path.join(settings.DIRNAME, "repositories"))

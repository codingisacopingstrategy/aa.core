from aacore import settings
from aacore.rdfutils import get_model


RDF_MODEL = get_model(settings.RDF_STORAGE_NAME, settings.RDF_STORAGE_DIR)

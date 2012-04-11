from aacore import settings
from aacore.rdfutils import get_model


RDF_MODEL = get_model(settings.RDF_STORAGE_NAME, settings.RDF_STORAGE_DIR)


def get_indexed_models():
    """
    Returns a list of the classes registered in settings.INDEXED_MODELS
    """
    models = []
    for model_name in settings.INDEXED_MODELS:
        try:
            (module_name, class_name) = model_name.rsplit(".", 1)
            module = __import__(module_name, fromlist=[class_name])
            klass = getattr(module, class_name)
            models.append(klass)
        except ImportError:
            print "ERROR IMPORTING", model_name
    return models

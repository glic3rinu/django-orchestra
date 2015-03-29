class ModelTranslation(object):
    """
    Collects all model fields that would be translated
    
    using 'makemessages --domain database' management command
    """
    _registry = {}
    
    @classmethod
    def register(cls, model, fields):
        if model in cls._registry:
            raise ValueError("Model %s already registered." % model.__name__)
        cls._registry[model] = fields

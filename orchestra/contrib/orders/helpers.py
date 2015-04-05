from django.core.exceptions import ObjectDoesNotExist

from orchestra.core import services


def get_related_object(origin, max_depth=2):
    """
    Introspects origin object and return the first related service object
    
    WARNING this is NOT an exhaustive search but a compromise between cost and
            flexibility. A more comprehensive approach may be considered if
            a use-case calls for it.
    """
    def related_iterator(node):
        for field in node._meta.virtual_fields:
            if hasattr(field, 'ct_field'):
                yield getattr(node, field.name)
        for field in node._meta.fields:
            if field.rel:
                try:
                    yield getattr(node, field.name)
                except ObjectDoesNotExist:
                    pass
    
    # BFS model relation transversal
    queue = [[origin]]
    while queue:
        models = queue.pop(0)
        if len(models) > max_depth:
            return None
        node = models[-1]
        if len(models) > 1:
            if type(node) in services:
                return node
        for related in related_iterator(node):
            if related and related not in models:
                new_models = list(models)
                new_models.append(related)
                queue.append(new_models)

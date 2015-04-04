import json

from rest_framework import serializers, exceptions


class OptionField(serializers.WritableField):
    """
    Dict-like representation of a OptionField
    A bit hacky, objects get deleted on from_native method and Serializer will
    need a custom override of restore_object method.
    """
    def to_native(self, value):
        """ dict-like representation of a Property Model"""
        return dict((prop.name, prop.value) for prop in value.all())
    
    def from_native(self, value):
        """ Convert a dict-like representation back to a WebOptionField """
        parent = self.parent
        related_manager = getattr(parent.object, self.source or 'options', False)
        properties = serializers.RelationsList()
        if value:
            model = getattr(parent.opts.model, self.source or 'options').related.model
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except:
                    raise exceptions.ParseError("Malformed property: %s" % str(value))
            if not related_manager:
                # POST (new parent object)
                return [model(name=n, value=v) for n,v in value.items()]
            # PUT
            to_save = []
            for (name, value) in value.items():
                try:
                    # Update existing property
                    prop = related_manager.get(name=name)
                except model.DoesNotExist:
                    # Create a new one
                    prop = model(name=name, value=value)
                else:
                    prop.value = value
                    to_save.append(prop.pk)
                properties.append(prop)
        
        # Discart old values
        if related_manager:
            properties._deleted = [] # Redefine class attribute
            for obj in related_manager.all():
                if not value or obj.pk not in to_save:
                    properties._deleted.append(obj)
        return properties

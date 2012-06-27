import django.dispatch

service_updated = django.dispatch.Signal(providing_args=["request", "instance", "message"])
#TODO Deprecate
service_created = django.dispatch.Signal(providing_args=["request", "contact", "instance","origin"])
service_deleted = django.dispatch.Signal(providing_args=["instance"])

# This signal is send by common.models.Collector in order to retrieve all the customized related objects 
# (no model related, only virtually related, ie. Names and Zones) that should be deleted when object is deleted.
collect_related_objects_to_delete = django.dispatch.Signal(providing_args=["object", "related_collection"])

# This signal is send in order to collect the dependencies of a future deletion, (reverse order form collect_related_objects_to_delete)
collect_dependencies = django.dispatch.Signal(providing_args=["object", "collection"])

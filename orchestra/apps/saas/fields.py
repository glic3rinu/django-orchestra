from django.contrib.contenttypes.fields import GenericRelation
from django.db import DEFAULT_DB_ALIAS

from orchestra.apps.databases.models import Database


class VirtualDatabaseRelation(GenericRelation):
    """ Delete related databases if any """
    def bulk_related_objects(self, objs, using=DEFAULT_DB_ALIAS):
        pks = []
        for obj in objs:
            if obj.database_id:
                pks.append(obj.database_id)
        if not pks:
            return []
        # TODO renamed to self.remote_field in django 1.8
        return self.rel.to._base_manager.db_manager(using).filter(pk__in=pks)

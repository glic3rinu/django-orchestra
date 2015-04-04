from django.contrib.contenttypes.fields import GenericRelation
from django.db import DEFAULT_DB_ALIAS


class VirtualDatabaseRelation(GenericRelation):
    """ Delete related databases if any """
    def bulk_related_objects(self, objs, using=DEFAULT_DB_ALIAS):
        pks = []
        for obj in objs:
            db_id = obj.data.get('db_id')
            if db_id:
                pks.append(db_id)
        if not pks:
            return []
        # TODO renamed to self.remote_field in django 1.8
        return self.rel.to._base_manager.db_manager(using).filter(pk__in=pks)


class VirtualDatabaseUserRelation(GenericRelation):
    """ Delete related databases if any """
    def bulk_related_objects(self, objs, using=DEFAULT_DB_ALIAS):
        pks = []
        for obj in objs:
            db_id = obj.data.get('db_user_id')
            if db_id:
                pks.append(db_id)
        if not pks:
            return []
        # TODO renamed to self.remote_field in django 1.8
        return self.rel.to._base_manager.db_manager(using).filter(pk__in=pks)

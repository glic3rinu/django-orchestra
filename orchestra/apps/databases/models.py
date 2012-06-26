from django.db import models
import settings

class Database(models.Model):
    name = models.CharField(max_length=60)
    type = models.CharField(max_length=16, choices=settings.DATABASE_TYPE_CHOICES, default=settings.DEFAULT_DATABASE_TYPE)
    
    class Meta:
        unique_together = ('name', 'type')
    
    def __unicode__(self):
        return self.name


class DBUser(models.Model):
    name = models.CharField(max_length=16)
    database = models.ManyToManyField(Database, through='databases.DB')
    password = models.CharField(max_length=41)
    host = models.CharField(max_length=60, default=settings.DEFAULT_HOST)
    # Data access	
    select = models.BooleanField(default=settings.DEFAULT_SELECT)
    delete = models.BooleanField(default=settings.DEFAULT_DELETE)
    insert = models.BooleanField(default=settings.DEFAULT_INSERT)
    update = models.BooleanField(default=settings.DEFAULT_UPDATE)
    # Structure access	
    create = models.BooleanField(default=settings.DEFAULT_CREATE)
    drop = models.BooleanField(default=settings.DEFAULT_DROP)
    alter = models.BooleanField(default=settings.DEFAULT_ALTER)
    index = models.BooleanField(default=settings.DEFAULT_INDEX)
    # Other	
    grant = models.BooleanField(default=settings.DEFAULT_GRANT)
    refer = models.BooleanField(default=settings.DEFAULT_REFER)
    lock = models.BooleanField(default=settings.DEFAULT_LOCK)

    class Meta:
        unique_together = ('name', 'host')
        
    def __unicode__(self):
        return self.name
        
        
class DB(models.Model):
    database = models.ForeignKey(Database)
    user = models.ForeignKey(DBUser)
    host = models.CharField(max_length=60, default=settings.DEFAULT_HOST)
    # Data access	
    select = models.BooleanField(default=settings.DEFAULT_SELECT)
    delete = models.BooleanField(default=settings.DEFAULT_DELETE)
    insert = models.BooleanField(default=settings.DEFAULT_INSERT)
    update = models.BooleanField(default=settings.DEFAULT_UPDATE)
    # Structure access	
    create = models.BooleanField(default=settings.DEFAULT_CREATE)
    drop = models.BooleanField(default=settings.DEFAULT_DROP)
    alter = models.BooleanField(default=settings.DEFAULT_ALTER)
    index = models.BooleanField(default=settings.DEFAULT_INDEX)
    # Other	
    grant = models.BooleanField(default=settings.DEFAULT_GRANT)
    refer = models.BooleanField(default=settings.DEFAULT_REFER)
    lock = models.BooleanField(default=settings.DEFAULT_LOCK)

    class Meta:
        unique_together = ('database', 'user', 'host')

    @property
    def contact(self):
        return self.database.contact


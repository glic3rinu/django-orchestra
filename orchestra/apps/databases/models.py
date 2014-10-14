import hashlib

from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core import validators, services

from . import settings


class Database(models.Model):
    """ Represents a basic database for a web application """
    MYSQL = 'mysql'
    POSTGRESQL = 'postgresql'
    
    name = models.CharField(_("name"), max_length=64, # MySQL limit
            validators=[validators.validate_name])
    users = models.ManyToManyField('databases.DatabaseUser',
            verbose_name=_("users"),related_name='databases')
#           through='databases.Role', 
    type = models.CharField(_("type"), max_length=32,
            choices=settings.DATABASES_TYPE_CHOICES,
            default=settings.DATABASES_DEFAULT_TYPE)
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='databases')
    
    class Meta:
        unique_together = ('name', 'type')
    
    def __unicode__(self):
        return "%s" % self.name
    
    @property
    def owner(self):
        """ database owner is the first user related to it """
        # Accessing intermediary model to get which is the first user
        users = Database.users.through.objects.filter(database_id=self.id)
        return users.order_by('-id').first().databaseuser


Database.users.through._meta.unique_together = (('database', 'databaseuser'),)

#class Role(models.Model):
#    database = models.ForeignKey(Database, verbose_name=_("database"),
#            related_name='roles')
#    user = models.ForeignKey('databases.DatabaseUser', verbose_name=_("user"),
#            related_name='roles')
##    is_owner = models.BooleanField(_("owner"), default=False)
#    
#    class Meta:
#        unique_together = ('database', 'user')
#    
#    def __unicode__(self):
#        return "%s@%s" % (self.user, self.database)
#    
#    @property
#    def is_owner(self):
#        return datatase.owner == self
#    
#    def clean(self):
#        if self.user.type != self.database.type:
#            msg = _("Database and user type doesn't match")
#            raise validators.ValidationError(msg)
#        roles = self.database.roles.values('id')
#        if not roles or (len(roles) == 1 and roles[0].id == self.id):
#            self.is_owner = True


class DatabaseUser(models.Model):
    MYSQL = 'mysql'
    POSTGRESQL = 'postgresql'
    
    username = models.CharField(_("username"), max_length=16, # MySQL usernames 16 char long
            validators=[validators.validate_name])
    password = models.CharField(_("password"), max_length=256)
    type = models.CharField(_("type"), max_length=32,
            choices=settings.DATABASES_TYPE_CHOICES,
            default=settings.DATABASES_DEFAULT_TYPE)
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='databaseusers')
    
    class Meta:
        verbose_name_plural = _("DB users")
        unique_together = ('username', 'type')
    
    def __unicode__(self):
        return self.username
    
    def get_username(self):
        return self.username
    
    def set_password(self, password):
        if self.type == self.MYSQL:
            # MySQL stores sha1(sha1(password).binary).hex
            binary = hashlib.sha1(password).digest()
            hexdigest = hashlib.sha1(binary).hexdigest()
            self.password = '*%s' % hexdigest.upper()
        else:
            raise TypeError("Database type '%s' not supported" % self.type)


services.register(Database)
services.register(DatabaseUser, verbose_name_plural=_("Database users"))

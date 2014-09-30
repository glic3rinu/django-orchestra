import hashlib

from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core import validators, services

from . import settings


class Database(models.Model):
    """ Represents a basic database for a web application """
    MYSQL = 'mysql'
    POSTGRESQL = 'postgresql'
    
    name = models.CharField(_("name"), max_length=128,
            validators=[validators.validate_name])
    users = models.ManyToManyField('databases.DatabaseUser',
            verbose_name=_("users"),
           through='databases.Role', related_name='users')
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
        self.users.get(is_owner=True)


class Role(models.Model):
    database = models.ForeignKey(Database, verbose_name=_("database"),
            related_name='roles')
    user = models.ForeignKey('databases.DatabaseUser', verbose_name=_("user"),
            related_name='roles')
    is_owner = models.BooleanField(_("owner"), default=False)
    
    class Meta:
        unique_together = ('database', 'user')
    
    def __unicode__(self):
        return "%s@%s" % (self.user, self.database)
    
    def clean(self):
        if self.user.type != self.database.type:
            msg = _("Database and user type doesn't match")
            raise validators.ValidationError(msg)


class DatabaseUser(models.Model):
    MYSQL = 'mysql'
    POSTGRESQL = 'postgresql'
    
    username = models.CharField(_("username"), max_length=128,
            validators=[validators.validate_name])
    password = models.CharField(_("password"), max_length=128)
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
            password = '*%s' % hexdigest.upper()
            self.password = password
        else:
            raise TypeError("Database type '%s' not supported" % self.type)


services.register(Database)
services.register(DatabaseUser, verbose_name_plural=_("Database users"))

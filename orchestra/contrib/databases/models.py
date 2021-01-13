import hashlib

from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core import validators

from . import settings


class Database(models.Model):
    """ Represents a basic database for a web application """
    MYSQL = 'mysql'
    POSTGRESQL = 'postgresql'
    
    name = models.CharField(_("name"), max_length=64, # MySQL limit
            validators=[validators.validate_name])
    users = models.ManyToManyField('databases.DatabaseUser', blank=True,
            verbose_name=_("users"),related_name='databases')
    type = models.CharField(_("type"), max_length=32,
            choices=settings.DATABASES_TYPE_CHOICES,
            default=settings.DATABASES_DEFAULT_TYPE)
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='databases')
    comments = models.TextField(default="", blank=True)
    
    class Meta:
        unique_together = ('name', 'type')
    
    def __str__(self):
        return "%s" % self.name
    
    @property
    def owner(self):
        """ database owner is the first user related to it """
        # Accessing intermediary model to get which is the first user
        users = Database.users.through.objects.filter(database_id=self.id)
        user = users.order_by('id').first()
        if user is not None:
            return user.databaseuser
        return None
    
    @property
    def active(self):
        return self.account.is_active


Database.users.through._meta.unique_together = (
    ('database', 'databaseuser'),
)


class DatabaseUser(models.Model):
    MYSQL = Database.MYSQL
    POSTGRESQL = Database.POSTGRESQL
    
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
    
    def __str__(self):
        return self.username
    
    def get_username(self):
        return self.username
    
    def set_password(self, password):
        if self.type == self.MYSQL:
            # MySQL stores sha1(sha1(password).binary).hex
            binary = hashlib.sha1(password.encode('utf-8')).digest()
            hexdigest = hashlib.sha1(binary).hexdigest()
            self.password = '*%s' % hexdigest.upper()
        else:
            raise TypeError("Database type '%s' not supported" % self.type)

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import settings


class BaseDatabase(models.Model):
    """ Base class containing fields needed by User and Database models """
    name = models.CharField(_("name"), unique=True, max_length=128)
    # Data access
    select = models.BooleanField(_("select"), default=settings.DATABASES_DEFAULT_SELECT)
    delete = models.BooleanField(_("delete"), default=settings.DATABASES_DEFAULT_DELETE)
    insert = models.BooleanField(_("insert"), default=settings.DATABASES_DEFAULT_INSERT)
    update = models.BooleanField(_("update"), default=settings.DATABASES_DEFAULT_UPDATE)
    # Structural access
    create = models.BooleanField(_("create"), default=settings.DATABASES_DEFAULT_CREATE)
    drop = models.BooleanField(_("drop"), default=settings.DATABASES_DEFAULT_DROP)
    alter = models.BooleanField(_("alter"), default=settings.DATABASES_DEFAULT_ALTER)
    index = models.BooleanField(_("index"), default=settings.DATABASES_DEFAULT_INDEX)
    # Other
    grant = models.BooleanField(_("grant"), default=settings.DATABASES_DEFAULT_GRANT)
    refer = models.BooleanField(_("refer"), default=settings.DATABASES_DEFAULT_REFER)
    lock = models.BooleanField(_("lock"), default=settings.DATABASES_DEFAULT_LOCK)
    
    class Meta:
        abstract = True


class User(BaseDatabase):
    password = models.CharField(_("password"), max_length=41)
    
    def __unicode__(self):
        return self.name


class Database(BaseDatabase):
    user = models.ForeignKey(User, verbose_name=_("user"))
    
    def __unicode__(self):
        return str(self.user)

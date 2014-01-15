from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import settings


# TODO validations and max_lengths!


class SystemUser(models.Model):
    """
    Represents the content of /etc/passwd UNIX file
    
    http://en.wikipedia.org/wiki/Passwd
    """
    
    uid = models.PositiveIntegerField("UID", primary_key=True)
    user = models.OneToOneField(get_user_model(), verbose_name=_("user"))
    group = models.ForeignKey(_("primary group"),
            default=settings.SYSTEMUSERS_DEFAULT_PRIMARY_GROUP_PK)
    home = models.CharField(_("home directory"), max_length=256,
            default=settings.SYSTEMUSERS_DEFAULT_BASE_HOMEDIR)
    description = models.CharField(_("description"), max_length=256)
    shell = models.CharField(_("shell"), max_length=256,
            default=settings.SYSTEMUSERS_DEFAULT_SHELL)
    ftp_only = models.BooleanField(_("FTP only"), default=False)
    
    def __unicode__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if not self.uid:
            # Assign UID
            try:
                self.uid = SystemUser.objects.all().order_by('-uid')[0].uid + 1
            except IndexError:
                self.uid = settings.SYSTEMUSERS_START_UID
        super(SystemUser, self).save(*args, **kwargs)
    
    @property
    def username(self):
        return self.user.username
    
    @property
    def gid(self):
        return self.group.gid
    
    @property
    def password(self):
        return self.user.password


class SystemGroup(models.Model):
    """ Represents the content of /etc/groups UNIX file """
    gid = models.PositiveIntegerField("GID", primary_key=True)
    name = models.CharField(_("name"), max_length=30)
    users = models.ManyToManyField(SystemUser, verbose_name=_("Users"), null=True,
            blank=True)
    
    def __unicode__(self):
        return self.name

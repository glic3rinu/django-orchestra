from django.contrib.auth.models import User
from django.db import models
import settings

class SystemUser(models.Model):
    """ /etc/passwd - Users for SuExec and ftp accounts. """ 
    user = models.OneToOneField(User, primary_key=True)
    shell = models.CharField(max_length=23, default=settings.SYSTEM_USER_DEFAULT_SHELL)
    uid = models.PositiveIntegerField(unique=True)
    primary_group = models.ForeignKey('SystemGroup', default=settings.SYSTEM_USER_DEFAULT_PRIMARY_GROUP_PK)
    homedir = models.CharField(max_length=255, default=settings.SYSTEM_USER_DEFAULT_BASE_HOMEDIR)
    only_ftp = models.BooleanField(default=False)

    def __unicode__(self):
        return self.username 

    def save(self, *args, **kwargs):
        if not self.uid:
            last = SystemUser.objects.all().order_by('-uid')[0].uid
            if not last:
                self.uid = settings.SYSTEM_USER_START_UID
            else:
                self.uid = last + 1
        super(SystemUser, self).save(*args, **kwargs)       

    @property
    def username(self):   
        return self.user.username


class SystemGroup(models.Model):
    """ /etc/groups """
    name = models.CharField(max_length=30)
    gid = models.PositiveIntegerField(unique=True)
    users = models.ManyToManyField(SystemUser, null=True, blank=True)
    
    def __unicode__(self):
        return self.name



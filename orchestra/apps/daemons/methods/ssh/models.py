from django.db import models
import settings

class SSHOption(models.Model):
    host = models.OneToOneField('daemons.Host')
    user = models.CharField("SSH User", max_length=32, default=settings.DEFAULT_SSH_USER, blank=True)
    password = models.CharField("SSH Password", max_length=64, blank=True)
    host_keys = models.CharField("SSH Host Keys", max_length=255, blank=True, default=settings.DEFAULT_SSH_HOST_KEYS)
    private_key = models.CharField("SSH Private Key", max_length=255, blank=True)
    port = models.IntegerField("SSH Port", default=settings.DEFAULT_SSH_PORT, blank=True)
    alternate_ip = models.IPAddressField("SSH IP", blank=True, help_text='Default host IP')
    
    def __unicode__(self):
        return str(self.host)
    
    @property
    def ip(self):
        return self.alternate_ip if self.alternate_ip else self.host.ip

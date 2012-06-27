from django.db import models

class List(models.Model):
    name = models.CharField(max_length=32)
    domain = models.ForeignKey('mail.VirtualDomain')
    admin = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    
    class Meta:
        unique_together = ('name', 'domain')
    
    def __unicode__(self):
        return "%s@%s" % (self.name, self.domain) 

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Jabber(models.Model):
    user = models.OneToOneField('users.User', verbose_name=_("user"),
            related_name='jabber')
    
    def __unicode__(self):
        return str(self.user)

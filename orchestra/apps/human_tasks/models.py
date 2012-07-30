from django.db import models
from django.utils.translation import ugettext as _


class Category(models.Model):
    name = models.CharField(max_length=32, unique=True)
    
    def __unicode__(self):
        return self.name


class Task(models.Model):
    category = models.ForeignKey(Category)
    description = models.CharField(max_length=256, blank=True)
    time = models.IntegerField(_('time in hours'))
    
    def __unicode__(self):
        return str(self.category)

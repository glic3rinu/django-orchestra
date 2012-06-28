from common.utils.python import _import
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models, connection
from common.utils.models import group_by
from django.utils.translation import ugettext as _
import settings


class ExtraField(models.Model):
    #TODO regex to check that name doesn't contains spaces
    name = models.CharField(max_length=32, unique=True)
    type = models.CharField(max_length=32, choices=settings.FIELD_TYPES, default=settings.DEFAUL_FIELD_TYPE)
    content_type = models.ForeignKey(ContentType)
    required = models.BooleanField(default=False)
    label = models.CharField(max_length=64, blank=True)
    raw_initial = models.CharField('initial', max_length=128, default=0, null=True, blank=True)
    help_text = models.CharField(max_length=255, blank=True)   
    widget = models.CharField(max_length=32, blank=True)
    error_messages = models.TextField(blank=True)

    def __unicode__(self):
        return self.name       

    def save(self, *args, **kwargs):
        if not self.pk:
            if hasattr(self.content_type.model_class(), self.name):
                raise AttributeError("Model already have this attribute name %s" % self.name)
                return
            if not self.label:
                self.label = self.name.replace('_', ' ').capitalize()
        super(ExtraField, self).save(*args, **kwargs)

    @classmethod
    def get_grouped(cls):
        #TODO: convert to Manager
        extra_fields = cls.objects.filter().order_by('content_type')
        return group_by(cls, 'content_type', extra_fields, queryset=False)

    @property
    def field_name(self):
        return "extra_field_%s" % self.pk

    @property
    def kwargs(self):
        kwargs = {}
        for kwarg in ('label', 'initial', 'help_text', 'widget', 'error_messages', 'required'):
            kwargs[kwarg] = getattr(self, kwarg) 
        return kwargs

    def get_form_field(self):
         field_class = _import('django.forms.fields.%s' % self.type)
         return field_class(**self.kwargs)
    
    @property
    def initial(self):
        field_class = _import('django.forms.fields.%s' % self.type)
        return field_class(required=False).to_python(self.raw_initial)


class ExtraValueManager(models.Manager):

    def by_object(self, obj, *args, **kwargs):
        ct = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=ct, object_id=obj.pk).filter(*args, **kwargs)
        
    def get_by_object_extra_field(self, obj, extra_field):
        ct = ContentType.objects.get_for_model(obj)
        return self.get(content_type=ct, object_id=obj.pk, extra_field=extra_field)
        

class ExtraValue(models.Model):
    extra_field = models.ForeignKey(ExtraField)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    raw_value = models.TextField(null=True)

    content_object = generic.GenericForeignKey('content_type', 'object_id')
    objects = ExtraValueManager()
    
    class Meta:
        unique_together = ('content_type', 'object_id', 'extra_field')
    
    def __unicode__(self):
        return str(self.extra_field)

    @property
    def value(self):
        field = self.extra_field.get_form_field()
        return field.to_python(self.raw_value)


def extravalue_register():
    """ Register this value extention to models, add reverse relation and attribute accessor"""
    cursor = connection.cursor()
    if 'extra_fields_extrafield' in connection.introspection.get_table_list(cursor):
        for field in ExtraField.objects.all():
            model = field.content_type.model_class()
            
            if not hasattr(model, 'extra_field_value'):
                generic.GenericRelation('extra_fields.ExtraValue').contribute_to_class(model, 'extra_field_value')

            @property
            def get_field_value(self, field_name=field.name):
                return ExtraValue.objects.by_object(obj=self, extra_field__name=field_name).get().value
    
            setattr(model, field.name, get_field_value)
            
extravalue_register()

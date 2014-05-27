from django.contrib import admin

from orchestra.core import services

from .models import Pack, Price, Rate


class RateInline(admin.TabularInline):
    model = Rate


class PriceAdmin(admin.ModelAdmin):
    inlines = [RateInline]
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Improve performance of account field and filter by account """
        if db_field.name == 'service':
            models = [model._meta.model_name for model in services.get().keys()]
            kwargs['queryset'] = db_field.rel.to.objects.filter(model__in=models)
        return super(PriceAdmin, self).formfield_for_dbfield(db_field, **kwargs)


admin.site.register(Price, PriceAdmin)

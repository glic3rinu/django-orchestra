from django.contrib import admin

from .models import Domain

class DomainAdmin(admin.ModelAdmin):
    pass

admin.site.register(Domain, DomainAdmin)

from django.contrib import admin

from .models import List

class ListAdmin(admin.ModelAdmin):
    pass

admin.site.register(List, ListAdmin)

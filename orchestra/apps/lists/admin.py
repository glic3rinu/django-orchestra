from django.contrib import admin
from models import List

class ListAdmin(admin.ModelAdmin):
    filter_fields_by_contact = ['domain__domain']

admin.site.register(List, ListAdmin)

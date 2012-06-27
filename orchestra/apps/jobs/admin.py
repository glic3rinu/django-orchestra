from django.contrib import admin
from models import Job, Category


class JobAdmin(admin.ModelAdmin):
    list_display = ('category', 'description', 'time',)


class CategoryAdmin(admin.ModelAdmin): pass


admin.site.register(Job, JobAdmin)
admin.site.register(Category, CategoryAdmin)


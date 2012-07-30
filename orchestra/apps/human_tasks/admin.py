from django.contrib import admin
from models import Task, Category


class TaskAdmin(admin.ModelAdmin):
    list_display = ('category', 'description', 'time',)


class CategoryAdmin(admin.ModelAdmin): pass


admin.site.register(Task, TaskAdmin)
admin.site.register(Category, CategoryAdmin)


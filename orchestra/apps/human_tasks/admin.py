from django.contrib import admin
from models import HumanTask, Category


class HumanTaskAdmin(admin.ModelAdmin):
    list_display = ('category', 'description', 'time',)


class CategoryAdmin(admin.ModelAdmin): pass


admin.site.register(HumanTask, HumanTaskAdmin)
admin.site.register(Category, CategoryAdmin)


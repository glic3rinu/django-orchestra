from django.contrib import admin

from .models import User, Database


class UserInline(admin.TabularInline):
    model = User


class DatabaseAdmin(admin.ModelAdmin):
    inlines = [UserInline]


admin.site.register(Database, DatabaseAdmin)

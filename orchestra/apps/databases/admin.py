from django.contrib import admin
from models import Database, DBUser, DB

class DBInline(admin.TabularInline):
    model = DB
    #TODO: unify this filter between serviceadmintabularinline and serviceaDMIN
    filter_fields_by_contact = ('user',)
    
    
class DatabaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']
    list_filter = ['type']
    inlines = [DBInline, ]
    

class DBAdmin(admin.ModelAdmin):
    list_display = ['host', 'database', 'user', 'select', 'delete', 'insert', 'update', 'create', 'drop', 'alter', 'index', 'grant', 'refer', 'lock']
    fieldsets = ((None,          {'fields': (('host',), 
                                             ('database',),
                                             ('user'),)}),
             ('Data access',     {'fields': (('select', 'delete', 'insert', 'update' ),)}),
             ('Structure access',{'fields': (('create', 'drop', 'alter', 'index'),)}),
             ('Other',           {'fields': (('grant', 'refer', 'lock'),)}),
             )
             

class DBUserAdmin(admin.ModelAdmin):
    list_display = ['name', 'host', 'select', 'delete', 'insert', 'update', 'create', 'drop', 'alter', 'index', 'grant', 'refer', 'lock']
    fieldsets = ((None,          {'fields': (('name',), 
                                             ('host',),
                                             ('password'),)}),
             ('Data access',     {'fields': (('select', 'delete', 'insert', 'update' ),)}),
             ('Structure access',{'fields': (('create', 'drop', 'alter', 'index'),)}),
             ('Other',           {'fields':(('grant', 'refer', 'lock'),)}),
             )
             

admin.site.register(Database, DatabaseAdmin)
admin.site.register(DB, DBAdmin)
admin.site.register(DBUser, DBUserAdmin)

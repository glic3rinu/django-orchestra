from django.contrib import admin

from .models import Order, QuotaStorage


class OrderAdmin(admin.ModelAdmin):
    pass


class QuotaStorageAdmin(admin.ModelAdmin):
    pass


admin.site.register(Order, OrderAdmin)
admin.site.register(QuotaStorage, QuotaStorageAdmin)

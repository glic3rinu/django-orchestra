from django.contrib import admin

from .models import PaymentSource, Transaction


admin.site.register(PaymentSource)
admin.site.register(Transaction)

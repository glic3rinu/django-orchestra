from django.contrib import admin

from orchestra.admin.utils import admin_link

from .models import Message, SMTPLog


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'state', 'priority', 'to_address', 'from_address', 'created_at', 'retries', 'last_retry'
    )


class SMTPLogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'message_link', 'result', 'date', 'log_message'
    )
    
    message_link = admin_link('message')


admin.site.register(Message, MessageAdmin)
admin.site.register(SMTPLog, SMTPLogAdmin)

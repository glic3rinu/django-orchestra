from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import admin_link, admin_colored, admin_date

from .models import Message, SMTPLog


COLORS = { 
    Message.QUEUED: 'purple',
    Message.SENT: 'green',
    Message.DEFERRED: 'darkorange',
    Message.FAILED: 'red',
    SMTPLog.SUCCESS: 'green',
    SMTPLog.FAILURE: 'red',
}


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'colored_state', 'priority', 'to_address', 'from_address', 'created_at_delta',
        'retries', 'last_retry_delta', 'num_logs',
    )
    list_filter = ('state', 'priority', 'retries')
    
    colored_state = admin_colored('state', colors=COLORS)
    created_at_delta = admin_date('created_at')
    last_retry_delta = admin_date('last_retry')
    
    def num_logs(self, instance):
        num = instance.logs__count
        url = reverse('admin:mailer_smtplog_changelist')
        url += '?&message=%i' % instance.pk
        return '<a href="%s">%d</a>' % (url, num)
    num_logs.short_description = _("Logs")
    num_logs.admin_order_field = 'logs__count'
    num_logs.allow_tags = True
    
    def get_queryset(self, request):
        qs = super(MessageAdmin, self).get_queryset(request)
        return qs.annotate(Count('logs'))


class SMTPLogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'message_link', 'colored_result', 'date_delta', 'log_message'
    )
    list_filter = ('result',)
    
    message_link = admin_link('message')
    colored_result = admin_colored('result', colors=COLORS, bold=False)
    date_delta = admin_date('date')


admin.site.register(Message, MessageAdmin)
admin.site.register(SMTPLog, SMTPLogAdmin)

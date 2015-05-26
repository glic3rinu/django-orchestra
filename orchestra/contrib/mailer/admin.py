from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import admin_link, admin_colored, admin_date, wrap_admin_view
from orchestra.contrib.tasks import task

from .engine import send_pending
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
        'display_subject', 'colored_state', 'priority', 'to_address', 'from_address',
        'created_at_delta', 'retries', 'last_retry_delta', 'num_logs',
    )
    list_filter = ('state', 'priority', 'retries')
    list_prefetch_related = ('logs__id')
    
    colored_state = admin_colored('state', colors=COLORS)
    created_at_delta = admin_date('created_at')
    last_retry_delta = admin_date('last_retry')
    
    def display_subject(self, instance):
        return instance.subject[:32]
    display_subject.short_description = _("Subject")
    display_subject.admin_order_field = 'subject'
    
    def num_logs(self, instance):
        num = instance.logs__count
        if num == 1:
            pk = instance.logs.all()[0].id
            url = reverse('admin:mailer_smtplog_change', args=(pk,))
        else:
            url = reverse('admin:mailer_smtplog_changelist')
            url += '?&message=%i' % instance.pk
        return '<a href="%s" onclick="return showAddAnotherPopup(this);">%d</a>' % (url, num)
    num_logs.short_description = _("Logs")
    num_logs.admin_order_field = 'logs__count'
    num_logs.allow_tags = True
    
    def get_urls(self):
        from django.conf.urls import url
        urls = super(MessageAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        urls.insert(0,
            url(r'^send-pending/$',
                wrap_admin_view(self, self.send_pending_view),
                name='%s_%s_send_pending' % info)
        )
        return urls
    
    def get_queryset(self, request):
        qs = super(MessageAdmin, self).get_queryset(request)
        return qs.annotate(Count('logs')).prefetch_related('logs')
    
    def send_pending_view(self, request):
        task(send_pending).apply_async()
        self.message_user(request, _("Pending messages are being sent on the background."))
        return redirect('..')
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'subject':
            kwargs['widget'] = forms.TextInput(attrs={'size':'100'})
        return super(MessageAdmin, self).formfield_for_dbfield(db_field, **kwargs)

class SMTPLogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'message_link', 'colored_result', 'date_delta', 'log_message'
    )
    list_filter = ('result',)
    fields = ('message_link', 'colored_result', 'date_delta', 'log_message')
    readonly_fields = fields
    
    message_link = admin_link('message')
    colored_result = admin_colored('result', colors=COLORS, bold=False)
    date_delta = admin_date('date')


admin.site.register(Message, MessageAdmin)
admin.site.register(SMTPLog, SMTPLogAdmin)

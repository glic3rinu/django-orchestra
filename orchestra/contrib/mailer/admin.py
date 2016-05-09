import base64
import email

from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import admin_link, admin_colored, admin_date, wrap_admin_view
from orchestra.contrib.tasks import task

from .actions import last
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


class MessageAdmin(ExtendedModelAdmin):
    list_display = (
        'display_subject', 'colored_state', 'priority', 'to_address', 'from_address',
        'created_at_delta', 'display_retries', 'last_try_delta',
    )
    list_filter = ('state', 'priority', 'retries')
    list_prefetch_related = ('logs',)
    search_fields = ('to_address', 'from_address', 'subject',)
    fieldsets = (
        (None, {
            'fields': ('state', 'priority', ('retries', 'last_try_delta', 'created_at_delta'),
                       'display_full_subject', 'display_from', 'display_to',
                       'display_content'),
        }),
        (_("Edit"), {
            'classes': ('collapse',),
            'fields': ('subject', 'from_address', 'to_address', 'content'),
        }),
    )
    readonly_fields = (
        'retries', 'last_try_delta', 'created_at_delta', 'display_full_subject',
        'display_to', 'display_from', 'display_content',
    )
    date_hierarchy = 'created_at'
    change_view_actions = (last,)
    
    colored_state = admin_colored('state', colors=COLORS)
    created_at_delta = admin_date('created_at')
    last_try_delta = admin_date('last_try')
    
    def display_subject(self, instance):
        subject = instance.subject
        if len(subject) > 64:
            return subject[:64] + '&hellip;'
        return subject
    display_subject.short_description = _("Subject")
    display_subject.admin_order_field = 'subject'
    display_subject.allow_tags = True
    
    def display_retries(self, instance):
        num_logs = instance.logs__count
        if num_logs == 1:
            pk = instance.logs.all()[0].id
            url = reverse('admin:mailer_smtplog_change', args=(pk,))
        else:
            url = reverse('admin:mailer_smtplog_changelist')
            url += '?&message=%i' % instance.pk
        return '<a href="%s" onclick="return showAddAnotherPopup(this);">%d</a>' % (url, instance.retries)
    display_retries.short_description = _("Retries")
    display_retries.admin_order_field = 'retries'
    display_retries.allow_tags = True
    
    def display_content(self, instance):
        part = email.message_from_string(instance.content)
        payload = part.get_payload()
        if isinstance(payload, list):
            for cpart in payload:
                cpayload = cpart.get_payload()
                if cpart.get_content_type().startswith('text/'):
                    part = cpart
                    payload = cpayload
                    if cpart.get_content_type() == 'text/html':
                        payload = '<div style="padding-left:110px">%s</div>' % payload
                        # prioritize HTML
                        break
        if part.get('Content-Transfer-Encoding') == 'base64':
            payload = base64.b64decode(payload)
            charset = part.get_charsets()[0]
            if charset:
                payload = payload.decode(charset)
        if part.get_content_type() == 'text/plain':
            payload = payload.replace('\n', '<br>').replace(' ', '&nbsp;')
        return payload
    display_content.short_description = _("Content")
    display_content.allow_tags = True
    
    def display_full_subject(self, instance):
        return instance.subject
    display_full_subject.short_description = _("Subject")
    
    def display_from(self, instance):
        return instance.from_address
    display_from.short_description = _("From")
    
    def display_to(self, instance):
        return instance.to_address
    display_to.short_description = _("To")
    
    def get_urls(self):
        from django.conf.urls import url
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        urls.insert(0,
            url(r'^send-pending/$',
                wrap_admin_view(self, self.send_pending_view),
                name='%s_%s_send_pending' % info)
        )
        return urls
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(Count('logs')).defer('content')
    
    def send_pending_view(self, request):
        task(send_pending).apply_async()
        self.message_user(request, _("Pending messages are being sent on the background."))
        return redirect('..')
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'subject':
            kwargs['widget'] = forms.TextInput(attrs={'size':'100'})
        return super().formfield_for_dbfield(db_field, **kwargs)


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

from django.template import Template, Context
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController
from orchestra.apps.resources import ServiceMonitor

from . import settings


class MailmanBackend(ServiceController):
    verbose_name = "Mailman"
    model = 'lists.List'


class MailmanTraffic(ServiceMonitor):
    model = 'lists.List'
    resource = ServiceMonitor.TRAFFIC
    
    def monitor(self, mail_list):
        context = self.get_context(mail_list)
        self.append(
            "SUBSCRIBERS=$(list_members %(list_name)s | wc -l)\n"
            "SIZE=$(grep ' post to %(list_name)s ' %(mailman_log)s \\\n"
            "       | awk '\"%(last_date)s\"<=$0 && $0<=\"%(current_date)s\"' \\\n"
            "       | sed 's/.*size=\([0-9]*\).*/\\1/' \\\n"
            "       | tr '\\n' '+' \\\n"
            "       | xargs -i echo {}0 )\n"
            "echo %(object_id)s $(( ${SIZE}*${SUBSCRIBERS} ))" % context)
    
    def get_context(self, mail_list):
        return {
            'mailman_log': settings.LISTS_MAILMAN_POST_LOG_PATH,
            'list_name': mail_list.name,
            'object_id': mail_list.pk,
            'last_date': timezone.localtime(self.get_last_date(mail_list)).strftime("%b %d %H:%M:%S"),
            'current_date': timezone.localtime(self.get_current_date()).strftime("%b %d %H:%M:%S"),
        }

import textwrap

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
    
    def prepare(self):
        current_date = timezone.localtime(self.current_date)
        current_date = current_date.strftime("%b %d %H:%M:%S")
        self.append(textwrap.dedent("""
            function monitor () {
                OBJECT_ID=$1
                LAST_DATE=$2
                LIST_NAME="$3"
                MAILMAN_LOG="$4"
                
                SUBSCRIBERS=$(list_members ${LIST_NAME} | wc -l)
                SIZE=$(grep ' post to ${LIST_NAME} ' "${MAILMAN_LOG}" \
                       | awk '\"$LAST_DATE\"<=$0 && $0<=\"%s\"' \
                       | sed 's/.*size=\([0-9]*\).*/\\1/' \
                       | tr '\\n' '+' \
                       | xargs -i echo {} )
                echo ${OBJECT_ID} $(( ${SIZE}*${SUBSCRIBERS} ))
            }""" % current_date))
    
    def monitor(self, mail_list):
        context = self.get_context(mail_list)
        self.append(
            'monitor %(object_id)i %(last_date)s "%(list_name)s" "%(log_file)s"' % context)
    
    def get_context(self, mail_list):
        last_date = timezone.localtime(self.get_last_date(mail_list.pk))
        return {
            'mailman_log': settings.LISTS_MAILMAN_POST_LOG_PATH,
            'list_name': mail_list.name,
            'object_id': mail_list.pk,
            'last_date': last_date.strftime("%b %d %H:%M:%S"),
        }

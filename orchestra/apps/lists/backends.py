from django.template import Template, Context

from orchestra.apps.orchestration import ServiceBackend


class MailmanBackend(ServiceBackend):
    verbose_name = "Mailman"
    model = 'lists.List'
    
    def save(self, mailinglist):
        pass

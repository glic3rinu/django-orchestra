from django.apps import AppConfig

from orchestra.core import accounts, administration


class IssuesConfig(AppConfig):
    name = 'orchestra.contrib.issues'
    verbose_name = "Issues"
    
    def ready(self):
        from .models import Queue, Ticket
        accounts.register(Ticket, icon='Ticket_star.png')
        administration.register(Queue, dashboard=False)

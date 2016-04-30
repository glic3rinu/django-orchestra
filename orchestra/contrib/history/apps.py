from django.apps import AppConfig

from orchestra.core import administration


class HistoryConfig(AppConfig):
    name = 'orchestra.contrib.history'
    verbose_name = 'History'
    
    def ready(self):
        from django.contrib.admin.models import LogEntry
        administration.register(
            LogEntry, verbose_name='History', verbose_name_plural='History', icon='History.png'
        )

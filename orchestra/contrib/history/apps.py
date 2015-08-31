from django import db
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
        # prevent loosing creation time on log entry edition
        action_time = LogEntry._meta.get_field_by_name('action_time')[0]
        action_time.auto_now = False
        action_time.auto_now_add = True

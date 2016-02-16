
### Quick start
0. Install orchestra following any of these methods:
    1. [PIP-only, Fast deployment setup (demo)](README.md#fast-deployment-setup)
    2. [Docker container (development)](INSTALLDEV.md)
    3. [Install on current system (production)](INSTALL.md)
1. Add the servers that you want to manage on `/admin/orchestration/servers` and copy orchestra's SSH pubkey to them
    `orchestra@panel:~ ssh-copy-id root@server.address`
2. Now configure service by service (domains, databases, webapps, websites...):
    1. Add the route through `/admin/orchestration/route/`
    2. Check and configure related settings on `/admin/settings/setting/`
    3. Configure related resources if needed `/resources/resource/`, like Account Disc limit and traffic.
    3. Test that everything works by creating and deleting services
    4. Do the same for the other services
3. Configure billing by adding services `/admin/services/service/add/` and plans `/admin/plans/plan/`
    1. Once a service is created hit the *Update orders* button


### Architecture
    Orchestration
    Orders


### Creating new services
    1. Think about if the service can fit into one of the existing models like: SaaS or WebApps, refere to the related documentation if that is the case.
    2. Create a new django app using startapp management command. For ilustrational purposes we will create a crontab services that will allow orchestra to manage user-based crontabs.
        `python3 manage.py startapp crontabs`
    3. Add the new *crontabs* app to the `INSTALLED_APPS` in your project's `settings.py`
    3. Create a `models.py` file with the data your service needs to keep in order to be managed by orchestra
    ```python
from django.db import models

class CrontabSchedule(models.Model):
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"))
    minute = models.CharField(_("minute"), max_length=64, default='*')
    hour = models.CharField(_("hour"), max_length=64, default='*')
    day_of_week = models.CharField(_("day of week"), max_length=64, default='*')
    day_of_month = models.CharField(_("day of month"), max_length=64, default='*')
    month_of_year = models.CharField(_("month of year"), max_length=64, default='*')

    class Meta:
        ordering = ('month_of_year', 'day_of_month', 'day_of_week', 'hour', 'minute')

    def __str__(self):
        rfield = lambda f: f and str(f).replace(' ', '') or '*'
        return "{0} {1} {2} {3} {4} (m/h/d/dM/MY)".format(
            rfield(self.minute), rfield(self.hour), rfield(self.day_of_week),
            rfield(self.day_of_month), rfield(self.month_of_year),
        )

class Crontab(models.Model):
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"))
    schedule = models.ForeignKey(CrontabSchedule, verbose_name=_("schedule"))
    description = models.CharField(_("description"), max_length=256, blank=True)
    command = models.TextField(_("content"))

    def __str__(self):
        return (self.description or self.command)[:32]
```
    
    4. Create a `admin.py` to enable the admin interface
        ```python
        from django.contrib import admin
        from .models import CrontabSchedule, Crontab

        class CrontabScheduleAdmin(admin.ModelAdmin):
            pass

        class CrontabAdmin(admin.ModelAdmin):
            pass

        admin.site.register(CrontabSchedule, CrontabScheduleAdmin)
        admin.site.register(Crontab, CrontabAdmin)
    
    
    5. Create a `api.py` to enable the REST API.
    6. Create a `backends.py` fiel with the needed backends for service orchestration and monitoring
        ```python
        import os
        import textwrap
        from django.utils.translation import ugettext_lazy as _
        from orchestra.contrib.orchestration import ServiceController, replace
        from orchestra.contrib.resources import ServiceMonitor

        class UNIXCronBackend(ServiceController):
            """
            Basic UNIX cron support.
            """
            verbose_name = _("UNIX cron")
            model = 'crons.CronTab'
            
            def prepare(self):
                super(UNIXCronBackend, self).prepare()
                self.accounts = set()
            
            def save(self, crontab):
                self.accounts.add(crontab.account)
            
            def delete(self, crontab):
                self.accounts.add(crontab.account)
            
            def commit(self):
                for account in self.accounts:
                    crontab = None
                    self.append("echo '' > %(crontab_path)s" % context)
                    chown
                    for crontab in account.crontabs.all():
                        self.append("
        #            if crontab is None:
        #                self.append("rm -f %(crontab_path)s" % context)
        ```
    7. Configure the routing







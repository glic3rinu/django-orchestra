from django.core.management import setup_environ
from ucp import settings
setup_environ(settings)


from ucp.resources.models import Monitor, Monitoring
from datetime import datetime

monitor = Monitor.objects.get(content_type__name='contact')
now = datetime.now()
last = obj.last_monitorization(monitor)
last = last.date if last else now

for monitoring in Monitoring.objetcs.filter(monitor__resource='Traffic', date__lt=now, date__gt=last).exclude(monitor=monitor):
    contact = monitoring.contact
    traffic[contact] = traffic.get(contact, 0) + monitoring.last

for contact, value in traffic.iteritems():
    #monitor.record(obj=contact, data=value, date=now)
    print contact, value


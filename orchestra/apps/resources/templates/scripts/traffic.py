from resources.models import Monitor, Monitoring
from contacts.models import Contact
from datetime import datetime

# The result of this template should be stored on result variable

contact = Contact.objects.get(pk={{ object.pk }})
monitor = Monitor.objects.get(pk={{ monitor.pk }})

ini = '{{ start_date|date:"Y-m-d H:i:s" }}'
end = '{{ end_date|date:"Y-m-d H:i:s" }}'
result = 0

for monitoring in Monitoring.objects.filter(monitor__resource='Traffic', date__lt=end, date__gt=ini).exclude(monitor=monitor):
    if monitoring.content_object.contact == contact:
        result += monitoring.last





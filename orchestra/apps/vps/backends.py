from django.utils.translation import ugettext_lazy as _

from orchestra.apps.resources import ServiceMonitor


class OpenVZDisk(ServiceMonitor):
    model = 'vps.VPS'
    resource = ServiceMonitor.DISK


class OpenVZMemory(ServiceMonitor):
    model = 'vps.VPS'
    resource = ServiceMonitor.MEMORY


class OpenVZTraffic(ServiceMonitor):
    model = 'vps.VPS'
    resource = ServiceMonitor.TRAFFIC



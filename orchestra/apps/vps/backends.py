from django.utils.translation import ugettext_lazy as _

from orchestra.apps.resources import ServiceMonitor


class OpenVZTraffic(ServiceMonitor):
    model = 'vps.VPS'
    resource = ServiceMonitor.TRAFFIC
    
    def process(self, line, obj):
        """ diff with last stored value """
        object_id, value = line.split()
        last = self.get_last_data(object_id)
        if not last or last.value > value:
            return object_id, value
        return object_id, value-last.value
    
    def monitor(self, container):
        """ Get OpenVZ container traffic on a Proxmox +2.0 cluster """
        context = self.get_context(container)
        self.append(
            "CONF=$(grep -r 'HOSTNAME=\"%(hostname)s\"' /etc/pve/nodes/*/openvz/*.conf)" % context)
        self.append('NODE=$(echo "${CONF}" | cut -d"/" -f5)')
        self.append('CTID=$(echo "${CONF}" | cut -d"/" -f7 | cur -d"\." -f1)')
        self.append(
            "ssh root@${NODE} vzctl exec ${CTID} cat /proc/net/dev \\\n"
            "    | grep venet0 \\\n"
            "    | awk -F: '{print $2}' \\\n"
            "    | awk '{print $1+$9}'")
    
    def get_context(self, container):
        return {
            'hostname': container.hostname,
        }

import decimal
import textwrap

from orchestra.contrib.orchestration import ServiceController
from orchestra.contrib.resources import ServiceMonitor


class ProxmoxOVZ(ServiceController):
    model = 'vps.VPS'
    
    RESOURCES = (
        ('memory', 'mem'),
        ('swap', 'swap'),
        ('disk', 'disk')
    )
    GET_PROXMOX_INFO = textwrap.dedent("""
        function get_vz_info () {
            hostname=$1
            version=$(pveversion | cut -d '/' -f2 | cut -d'.' -f1)
            if [[ $version -lt 2 ]]; then
                conf=$(grep "CID\\|:$hostname:" /var/lib/pve-manager/vzlist | grep -B1 ":$hostname:")
                CID=$(echo "$conf" | head -n1 | cut -d':' -f2)
                CTID=$(echo "$conf" | tail -n1 | cut -d':' -f1)
                node=$(pveca -l | grep "^\\s*$CID\\s*:" | awk {'print $3'})
            else
                conf=$(grep -r "HOSTNAME=\\"$hostname\\"" /etc/pve/nodes/*/openvz/*.conf)
                node=$(echo "${conf}" | cut -d"/" -f5)
                CTID=$(echo "${conf}" | cut -d"/" -f7 | cut -d"\\." -f1)
            fi
            echo $CTID $node
        }""")
    
    def prepare(self):
        super(ProxmoxOVZ, self).prepare()
        self.append(self.GET_PROXMOX_INFO)
    
    def get_vzset_args(self, vps):
        args = []
        for resource, arg_name in self.RESOURCES:
            try:
                allocation = getattr(vps.resources, resource).allocated
            except AttributeError:
                pass
            else:
                args.append('--%s %i' % (arg_name, allocation))
        return ' '.join(args)
    
    def save(self, vps):
        context = self.get_context(vps)
        self.append('info=( $(get_vz_info %(hostname)s) )' % context)
        vzset_args = self.get_vzset_args(vps)
        if vzset_args:
            context['vzset_args'] = vzset_args
            self.append(textwrap.dedent("""\
                cat << EOF | ssh root@${info[1]}
                    pvectl vzset ${info[0]} %(vzset_args)s
                EOF""") % context
            )
        if hasattr(vps, 'password'):
            context['password'] = vps.password.replace('$', '\\$')
            self.append(textwrap.dedent("""\
                cat << EOF | ssh root@${info[1]}
                    echo 'root:%(password)s' | vzctl exec ${info[0]} chpasswd -e
                EOF""") % context
            )
    def get_context(self, vps):
        return {
            'hostname': vps.hostname,
        }


# TODO rename to proxmox
class OpenVZTraffic(ServiceMonitor):
    model = 'vps.VPS'
    resource = ServiceMonitor.TRAFFIC
    monthly_sum_old_values = True
    
    def prepare(self):
        super(OpenVZTraffic, self).prepare()
        self.append(ProxmoxOVZ.GET_PROXMOX_INFO)
        self.append(textwrap.dedent("""
            function monitor () {
                object_id=$1
                hostname=$2
                info=( $(get_vz_info $hostname) )
                cat << EOF | ssh root@${info[1]}
                    vzctl exec ${info[0]} cat /proc/net/dev \\
                        | grep venet0 \\
                        | tr ':' ' ' \\
                        | awk '{sum=\\$2+\\$10} END {printf ("$object_id %0.0f\\n", sum)}'
            EOF
            }
            """)
        )
    
    def process(self, line):
        """ diff with last stored state """
        object_id, value, state = super(OpenVZTraffic, self).process(line)
        value = decimal.Decimal(value)
        last = self.get_last_data(object_id)
        if not last or last.state > value:
            return object_id, value, value
        return object_id, value-last.state, value
    
    def monitor(self, vps):
        """ Get OpenVZ container traffic on a Proxmox cluster """
        context = self.get_context(vps)
        self.append('monitor %(object_id)s %(hostname)s' % context)
    
    def get_context(self, vps):
        return {
            'object_id': vps.id,
            'hostname': vps.hostname,
        }

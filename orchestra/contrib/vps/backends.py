import decimal
import textwrap

from orchestra.contrib.orchestration import ServiceController
from orchestra.contrib.resources import ServiceMonitor

from . import settings


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
    
    def get_vzset_args(self, context):
        args = list(settings.VPS_DEFAULT_VZSET_ARGS)
        for resource, arg_name in self.RESOURCES:
            try:
                allocation = context[resource]
            except KeyError:
                pass
            else:
                args.append('--%s %i' % (arg_name, allocation))
        return ' '.join(args)
    
    def run_ssh_commands(self, ssh_commands):
        commands = '\n    '.join(ssh_commands)
        self.append(textwrap.dedent("""\
            cat << EOF | ssh root@${info[1]}
                %s
            EOF""") % commands
        )
    
    def save(self, vps):
        # TODO create the container
        context = self.get_context(vps)
        self.append(textwrap.dedent("""
            info=( $(get_vz_info %(hostname)s) )
            echo "Managing ${info[@]}"\
            """) % context
        )
        ssh_commands = []
        vzset_args = self.get_vzset_args(context)
        if vzset_args:
            context['vzset_args'] = vzset_args
            ssh_commands.append("pvectl vzset ${info[0]} %(vzset_args)s" % context)
        if hasattr(vps, 'password'):
            context['password'] = vps.password.replace('$', '\\$')
            ssh_commands.append(textwrap.dedent("""\
                echo 'root:%(password)s' \\
                    | chroot /var/lib/vz/private/${info[0]} chpasswd -e""") % context
            )
        self.run_ssh_commands(ssh_commands)
    
    def get_context(self, vps):
        context = {
            'hostname': vps.hostname,
        }
        for resource, __ in self.RESOURCES:
            try:
                allocation = getattr(vps.resources, resource).allocated
            except AttributeError:
                pass
            else:
                context[resource] = allocation
        return context


class ProxmoxOpenVZTraffic(ServiceMonitor):
    model = 'vps.VPS'
    resource = ServiceMonitor.TRAFFIC
    monthly_sum_old_values = True
    GET_PROXMOX_INFO = ProxmoxOVZ.GET_PROXMOX_INFO

    def prepare(self):
        super(ProxmoxOpenVZTraffic, self).prepare()
        self.append(self.GET_PROXMOX_INFO)
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
        object_id, value, state = super(ProxmoxOpenVZTraffic, self).process(line)
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


class LxcController(ServiceController):
    model = 'vps.VPS'

    RESOURCES = (
        ('memory', 'mem'),
        ('disk', 'disk'),
        ('vcpu', 'vcpu')
    )

    def prepare(self):
        super(LxcController, self).prepare()

    def save(self, vps):
        # TODO create the container
        pass



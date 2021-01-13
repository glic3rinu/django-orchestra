import re
import socket
import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController
from orchestra.contrib.orchestration import Operation
from orchestra.utils.python import OrderedSet

from . import settings
from .models import Record, Domain


class Bind9MasterDomainController(ServiceController):
    """
    Bind9 zone and config generation.
    It auto-discovers slave Bind9 servers based on your routing configuration and NS servers.
    """
    CONF_PATH = settings.DOMAINS_MASTERS_PATH
    
    verbose_name = _("Bind9 master domain")
    model = 'domains.Domain'
    related_models = (
        ('domains.Record', 'domain__origin'),
        ('domains.Domain', 'origin'),
    )
    ignore_fields = ('serial',)
    doc_settings = (settings,
        ('DOMAINS_MASTERS_PATH',)
    )
    
    @classmethod
    def is_main(cls, obj):
        """ work around Domain.top self relationship """
        if super(Bind9MasterDomainController, cls).is_main(obj):
            return not obj.top
    
    def save(self, domain):
        context = self.get_context(domain)
        domain.refresh_serial()
        self.update_zone(domain, context)
        self.update_conf(context)
    
    def update_zone(self, domain, context):
        context['zone'] = ';; %(banner)s\n' % context
        context['zone'] += domain.render_zone()
        self.append(textwrap.dedent("""\
            # Generate %(name)s zone file
            cat << 'EOF' > %(zone_path)s.tmp
            %(zone)s
            EOF
            diff -N -I'^\s*;;' %(zone_path)s %(zone_path)s.tmp || UPDATED=1
            # Because bind reload will not display any fucking error
            named-checkzone -k fail -n fail %(name)s %(zone_path)s.tmp
            mv %(zone_path)s.tmp %(zone_path)s\
            """) % context
        )
    
    def update_conf(self, context):
        self.append(textwrap.dedent("""
            # Update bind config file for %(name)s
            read -r -d '' conf << 'EOF' || true
            %(conf)s
            EOF
            sed '/zone "%(name)s".*/,/^\s*};\s*$/!d' %(conf_path)s | diff -B -I"^\s*//" - <(echo "${conf}") || {
                sed -i -e '/zone\s\s*"%(name)s".*/,/^\s*};/d' \\
                       -e 'N; /^\s*\\n\s*$/d; P; D' %(conf_path)s
                echo "${conf}" >> %(conf_path)s
                UPDATED=1
            }""") % context
        )
        self.append(textwrap.dedent("""\
            # Delete ex-top-domains that are now subdomains
            sed -i -e '/zone\s\s*".*\.%(name)s".*/,/^\s*};\s*$/d' \\
                   -e 'N; /^\s*\\n\s*$/d; P; D' %(conf_path)s""") % context
        )
        if 'zone_path' in context:
            context['zone_subdomains_path'] = re.sub(r'^(.*/)', r'\1*.', context['zone_path'])
            self.append('rm -f -- %(zone_subdomains_path)s' % context)
    
    def delete(self, domain):
        context = self.get_context(domain)
        self.append('# Delete zone file for %(name)s' % context)
        self.append('rm -f -- %(zone_path)s;' % context)
        self.delete_conf(context)
    
    def delete_conf(self, context):
        if context['name'][0] in ('*', '_'):
            # These can never be top level domains
            return
        self.append(textwrap.dedent("""
            # Delete config for %(name)s
            sed -e '/zone\s\s*"%(name)s".*/,/^\s*};\s*$/d' \\
                -e 'N; /^\s*\\n\s*$/d; P; D' %(conf_path)s > %(conf_path)s.tmp""") % context
        )
        self.append('diff -B -I"^\s*//" %(conf_path)s.tmp %(conf_path)s || UPDATED=1' % context)
        self.append('mv %(conf_path)s.tmp %(conf_path)s' % context)
    
    def commit(self):
        """ reload bind if needed """
        self.append(textwrap.dedent("""
            # Apply changes
            if [[ $UPDATED == 1 ]]; then
                rm /etc/bind/master/*jnl || true;  service bind9 restart
            fi""")
        )
    
    def get_servers(self, domain, backend):
        """ Get related server IPs from registered backend routes """
        from orchestra.contrib.orchestration.manager import router
        operation = Operation(backend, domain, Operation.SAVE)
        servers = []
        for route in router.objects.get_for_operation(operation):
            servers.append(route.host.get_ip())
        return servers
    
    def get_masters_ips(self, domain):
        ips = list(settings.DOMAINS_MASTERS)
        if not ips:
            ips += self.get_servers(domain, Bind9MasterDomainController)
        return OrderedSet(sorted(ips))
    
    def get_slaves(self, domain):
        ips = []
        masters_ips = self.get_masters_ips(domain)
        records = domain.get_records()
        # Slaves from NS
        for record in records.by_type(Record.NS):
            hostname = record.value.rstrip('.')
            # First try with a DNS query, a more reliable source
            try:
                addr = socket.gethostbyname(hostname)
            except socket.gaierror:
                # check if hostname is declared
                try:
                    domain = Domain.objects.get(name=hostname)
                except Domain.DoesNotExist:
                    continue
                else:
                    # default to domain A record address
                    addr = records.by_type(Record.A)[0].value
            if addr not in masters_ips:
                ips.append(addr)
        # Slaves from internal networks
        if not settings.DOMAINS_MASTERS:
            for server in self.get_servers(domain, Bind9SlaveDomainController):
                ips.append(server)
        return OrderedSet(sorted(ips))
    
    def get_context(self, domain):
        slaves = self.get_slaves(domain)
        context = {
            'name': domain.name,
            'zone_path': settings.DOMAINS_ZONE_PATH % {'name': domain.name},
            'subdomains': domain.subdomains.all(),
            'banner': self.get_banner(),
            'slaves': '; '.join(slaves) or 'none',
            'also_notify': '; '.join(slaves) + ';' if slaves else '',
            'conf_path': self.CONF_PATH,
            'dns2136_address_match_list': domain.dns2136_address_match_list
        }
        context['conf'] = textwrap.dedent("""\
            zone "%(name)s" {
                // %(banner)s
                type master;
                file "%(zone_path)s";
                allow-transfer { %(slaves)s; };
                also-notify { %(also_notify)s };
                allow-update { %(dns2136_address_match_list)s };
                notify yes;
            };""") % context
        return context


class Bind9SlaveDomainController(Bind9MasterDomainController):
    """
    Generate the configuartion for slave servers
    It auto-discover the master server based on your routing configuration or you can use
    DOMAINS_MASTERS to explicitly configure the master.
    """
    CONF_PATH = settings.DOMAINS_SLAVES_PATH
    
    verbose_name = _("Bind9 slave domain")
    related_models = (
        ('domains.Domain', 'origin'),
    )
    doc_settings = (settings,
        ('DOMAINS_MASTERS', 'DOMAINS_SLAVES_PATH')
    )
    def save(self, domain):
        context = self.get_context(domain)
        self.update_conf(context)
    
    def delete(self, domain):
        context = self.get_context(domain)
        self.delete_conf(context)
    
    def commit(self):
        self.append(textwrap.dedent("""
            # Apply changes
            if [[ $UPDATED == 1 ]]; then
                # Async restart, ideally after master
                nohup bash -c 'sleep 1 && service bind9 reload' &> /dev/null &
            fi""")
        )
    
    def get_context(self, domain):
        context = {
            'name': domain.name,
            'banner': self.get_banner(),
            'subdomains': domain.subdomains.all(),
            'masters': '; '.join(self.get_masters_ips(domain)) or 'none',
            'conf_path': self.CONF_PATH,
        }
        context['conf'] = textwrap.dedent("""\
            zone "%(name)s" {
                // %(banner)s
                type slave;
                file "%(name)s";
                masters { %(masters)s; };
                allow-notify { %(masters)s; };
            };""") % context
        return context

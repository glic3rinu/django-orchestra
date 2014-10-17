import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController
from orchestra.utils.python import AttrDict

from . import settings


class Bind9MasterDomainBackend(ServiceController):
    verbose_name = _("Bind9 master domain")
    model = 'domains.Domain'
    related_models = (
        ('domains.Record', 'domain__origin'),
        ('domains.Domain', 'origin'),
    )
    ignore_fields = ['serial']
    
    @classmethod
    def is_main(cls, obj):
        """ work around Domain.top self relationship """
        if super(Bind9MasterDomainBackend, cls).is_main(obj):
            return not obj.top
    
    def save(self, domain):
        context = self.get_context(domain)
        domain.refresh_serial()
        context['zone'] = ';; %(banner)s\n' % context
        context['zone'] += domain.render_zone()
        self.append(textwrap.dedent("""\
            {
                echo -e '%(zone)s' | diff -N -I'^\s*;;' %(zone_path)s -
            } || {
                echo -e '%(zone)s' > %(zone_path)s
                UPDATED=1
            }""" % context
        ))
        self.update_conf(context)
    
    def update_conf(self, context):
        self.append(textwrap.dedent("""\
            cat -s <(sed -e 's/^};/};\\n/' %(conf_path)s) | \\
                awk -v s=pangea.cat 'BEGIN { RS=""; s="zone \\""s"\\"" } $0~s{ print }' | \\
            diff -B -I"^\s*//" - <(echo '%(conf)s') || {
                cat -s <(sed -e 's/^};/};\\n/' %(conf_path)s) | \\
                    awk -v s="%(name)s" 'BEGIN { RS=""; s="zone \\""s"\\"" } $0!~s{ print $0"\\n" }' \\
                    > %(conf_path)s.tmp
                echo -e '%(conf)s' >> %(conf_path)s.tmp
                mv %(conf_path)s.tmp %(conf_path)s
                UPDATED=1
            }""" % context
        ))
        for subdomain in context['subdomains']:
            context['name'] = subdomain.name
            self.delete(subdomain)
    
    def delete(self, domain):
        context = self.get_context(domain)
        self.append('rm -f %(zone_path)s;' % context)
        self.delete_conf(context)
    
    def delete_conf(self, context):
        if context['name'][0] in ('*', '_'):
            # These can never be top level domains
            return
        self.append(textwrap.dedent("""\
            cat -s <(sed -e 's/^};/};\\n/' %(conf_path)s) | \\
                awk -v s="%(name)s" 'BEGIN { RS=""; s="zone \\""s"\\"" } $0!~s{ print $0"\\n" }' \\
                > %(conf_path)s.tmp""" % context
        ))
        self.append('diff -B -I"^\s*//" %(conf_path)s.tmp %(conf_path)s || UPDATED=1' % context)
        self.append('mv %(conf_path)s.tmp %(conf_path)s' % context)
    
    def commit(self):
        """ reload bind if needed """
        self.append('[[ $UPDATED == 1 ]] && service bind9 reload')
    
    def get_servers(self, domain, backend):
        from orchestra.apps.orchestration.models import Route
        operation = AttrDict(backend=backend, action='save', instance=domain)
        servers = []
        for server in Route.get_servers(operation):
            servers.append(server.get_ip())
        return servers
    
    def get_slaves(self, domain):
        return self.get_servers(domain, Bind9SlaveDomainBackend)
    
    def get_context(self, domain):
        context = {
            'name': domain.name,
            'zone_path': settings.DOMAINS_ZONE_PATH % {'name': domain.name},
            'subdomains': domain.subdomains.all(),
            'banner': self.get_banner(),
            'slaves': '; '.join(self.get_slaves(domain)) or 'none',
        }
        context.update({
            'conf_path': settings.DOMAINS_MASTERS_PATH,
            'conf': textwrap.dedent("""
                zone "%(name)s" {
                    // %(banner)s
                    type master;
                    file "%(zone_path)s";
                    allow-transfer { %(slaves)s; };
                };""" % context)
        })
        return context


class Bind9SlaveDomainBackend(Bind9MasterDomainBackend):
    verbose_name = _("Bind9 slave domain")
    related_models = (
        ('domains.Domain', 'origin'),
    )
    
    def save(self, domain):
        context = self.get_context(domain)
        self.update_conf(context)
    
    def delete(self, domain):
        context = self.get_context(domain)
        self.delete_conf(context)
    
    def commit(self):
        """ ideally slave should be restarted after master """
        self.append('[[ $UPDATED == 1 ]] && { sleep 1 && service bind9 reload; } &')
    
    def get_masters(self, domain):
        return self.get_servers(domain, Bind9MasterDomainBackend)
    
    def get_context(self, domain):
        context = {
            'name': domain.name,
            'banner': self.get_banner(),
            'subdomains': domain.subdomains.all(),
            'masters': '; '.join(self.get_masters(domain)) or 'none',
        }
        context.update({
            'conf_path': settings.DOMAINS_SLAVES_PATH,
            'conf': textwrap.dedent("""
                zone "%(name)s" {
                    // %(banner)s
                    type slave;
                    file "%(name)s";
                    masters { %(masters)s; };
                    allow-notify { %(masters)s; };
                };""" % context)
        })
        return context

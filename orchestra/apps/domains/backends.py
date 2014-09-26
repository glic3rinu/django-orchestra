from django.utils.translation import ugettext_lazy as _

from . import settings

from orchestra.apps.orchestration import ServiceController


class Bind9MasterDomainBackend(ServiceController):
    verbose_name = _("Bind9 master domain")
    model = 'domains.Domain'
    related_models = (
        ('domains.Record', 'domain__origin'),
        ('domains.Domain', 'origin'),
    )
    
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
        self.append("{ echo -e '%(zone)s' | diff -N -I'^;;' %(zone_path)s - ; } ||"
                    "   { echo -e '%(zone)s' > %(zone_path)s; UPDATED=1; }" % context)
        self.update_conf(context)
    
    def update_conf(self, context):
        self.append("grep '\s*zone\s*\"%(name)s\"\s*{' %(conf_path)s > /dev/null ||"
                    "   { echo -e '%(conf)s' >> %(conf_path)s; UPDATED=1; }" % context)
        for subdomain in context['subdomains']:
            context['name'] = subdomain.name
            self.delete_conf(context)
    
    def delete(self, domain):
        context = self.get_context(domain)
        self.append('rm -f %(zone_path)s;' % context)
        self.delete_conf(context)
    
    def delete_conf(self, context):
        self.append('awk -v s=%(name)s \'BEGIN {'
                    '  RS=""; s="zone \\""s"\\""'
                    '} $0!~s{ print $0"\\n" }\' %(conf_path)s > %(conf_path)s.tmp'
                    % context)
        self.append('diff -I"^\s*//" %(conf_path)s.tmp %(conf_path)s || UPDATED=1' % context)
        self.append('mv %(conf_path)s.tmp %(conf_path)s' % context)
    
    def commit(self):
        """ reload bind if needed """
        self.append('[[ $UPDATED == 1 ]] && service bind9 reload')
    
    def get_context(self, domain):
        context = {
            'name': domain.name,
            'zone_path': settings.DOMAINS_ZONE_PATH % {'name': domain.name},
            'subdomains': domain.get_subdomains(),
            'banner': self.get_banner(),
        }
        context.update({
            'conf_path': settings.DOMAINS_MASTERS_PATH,
            'conf': 'zone "%(name)s" {\n'
                    '    // %(banner)s\n'
                    '    type master;\n'
                    '    file "%(zone_path)s";\n'
                    '};\n' % context
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
    
    def get_context(self, domain):
        context = {
            'name': domain.name,
            'masters': '; '.join(settings.DOMAINS_MASTERS),
            'subdomains': domain.get_subdomains()
        }
        context.update({
            'conf_path': settings.DOMAINS_SLAVES_PATH,
            'conf': 'zone "%(name)s" {\n'
                    '    type slave;\n'
                    '    file "%(name)s";\n'
                    '    masters { %(masters)s; };\n'
                    '};\n' % context
        })
        return context

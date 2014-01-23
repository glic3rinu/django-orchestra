import os

from django.utils.translation import ugettext_lazy as _

from orchestra.core.backends import ServiceBackend


class MasterBindBackend(ServiceBackend):
    name = _("master Bind")
    verbose_name = _("master Bind")
    models = ['zones.Zone', 'zones.Record']
    
    def save(self, zone):
        template = Template(
            "{{ zone.origin }}.  IN  SOA {{ zone.primary_ns }}. {{ zone.hostmaster_email }}. (\n"
            "       {{ zone.serial }}\t; serial number\n"
            "       {{ zone.slave_refresh }}\t; slave refresh\n"
            "       {{ zone.slave_retry }}\t; slave retry time in case of problem\n"
            "       {{ zone.slave_expiration }}\t; slave expiration time\n"
            "       {{ zone.min_caching_time }}\t; maximum caching time in case of failed lookups\n"
            "   )\n"
            "{% for record in zone.records %}"
            "{{ record.name }}\t\tIN\t{{ record.type }}\t{{ record.data }}\n"
            "{% endfor %}")
        context = self.get_context(zone)
        context.update({ 'content': template.render(Context({'zone': zone})) })
        self.append("{ echo -e '%(content)s' | diff %(path)s - ; } ||"
                    "   { echo -e '%(content)s' > %(path)s; UPDATED=1;}" % context)
        self.append("grep '\s*zone\s*\"%(name)s\"\s*{' %(master)s ||"
                    "   echo -e %(conf)s >> %(master)s" % context)
    
    def delete(self, zone):
        context = self.get_context(zone)
        self.append('rm -f %(path)s; UPDATED=1' % context)
        self.append('sed -i "s/\s*zone\s*"%(name)s"\s*{.*};//" %(master)s' % context)
     
    def reload(self, *zone):
        """ just make it commit """
        self.append('$UPDATED=1')
    
    def commit(self):
        """ reload bind after all the configuration has been generated (bulk support) """
        self.append('$UPDATED && service bind9 reload')
    
    def get_context(self, zone):
        context = {
            'name': zone.name,
            'path': os.path.join(settings.DNS_ZONE_FILE_PATH, zone.name),
            'master': settings.DNS_ZONE_MASTER_PATH,
        }
        context.update({
            'conf': 'zone "%(name)s" {\n'
                    '   type master;\n'
                    '   file "%(path)s";\n'
                    '};\n' % context
        })
        return context


class SlaveBindBackend(MasterBindBackend):
    name = _("slave Bind")
    verbose_name = _("Slave Bind")
    
    def save(self, zone):
        self.append('update or create slave')
    
    def delete(self, zone):
        self.append('delete secondary')

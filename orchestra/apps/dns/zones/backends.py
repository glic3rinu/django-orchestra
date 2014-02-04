import os

from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _

from orchestra.orchestration import ServiceBackend

from . import settings


class MasterBindBackend(ServiceBackend):
    name = 'master-Bind'
    verbose_name = _("master Bind")
    model = 'zones.Zone'
    related_models = (('zones.Record', 'zone'),)
    
    def save(self, zone):
        template = Template(
            "{{ zone.name }}.  IN  SOA {{ zone.name_server }}. {{ zone.formatted_hostmaster }}. (\n"
            "       {{ zone.serial }}\t; serial number\n"
            "       {{ zone.refresh }}\t; slave refresh\n"
            "       {{ zone.retry }}\t; slave retry time in case of problem\n"
            "       {{ zone.expiration }}\t; slave expiration time\n"
            "       {{ zone.min_caching_time }}\t; maximum caching time in case of failed lookups\n"
            "   )\n"
            "{% for record in zone.records.all %}"
            "{{ record.name }}\t\tIN\t{{ record.type }}\t{{ record.value }}\n"
            "{% endfor %}")
        context = self.get_context(zone)
        context.update({ 'content': template.render(Context({'zone': zone})) })
        self.append("{ echo -e '%(content)s' | diff %(path)s - ; } ||"
                    "   { echo -e '%(content)s' > %(path)s; UPDATED=1; }" % context)
        self.append("grep '\s*zone\s*\"%(name)s\"\s*{' %(master)s ||"
                    "   echo -e '%(conf)s' >> %(master)s" % context)
    
    def delete(self, zone):
        context = self.get_context(zone)
        self.append('rm -f %(path)s; UPDATED=1' % context)
        self.append('sed -i "s/\s*zone\s*"%(name)s"\s*{.*};//" %(master)s' % context)
     
    def reload(self, *zone):
        """ just make it commit """
        self.append('$UPDATED=1')
    
    def commit(self):
        """ reload bind if needed """
        self.append('[[ $UPDATED == 1 ]] && service bind9 reload')
    
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
    name = 'slave-Bind'
    verbose_name = _("Slave Bind")
    
    def save(self, zone):
        self.append('update or create slave')
    
    def delete(self, zone):
        self.append('delete secondary')

import os

from django.utils.translation import ugettext_lazy as _
from django.template import Template, Context

from orchestra.orchestration import ServiceBackend


class Apache2Backend(ServiceBackend):
    name = 'Apache2'
    verbose_name = _("Apache2")
    model = 'webs.Web'
    
    BASE_APACHE_PATH = '/etc/apache2'
    BASE_APACHE_LOGS = '/var/log/apache2/virtual/'
    
    def save(self, web):
        template = Template(
            "<VirtualHost *:{{ web.port }}\n"
            "    DocumentRoot {{ web.root }}\n"
            "    ServerName {{ web.domains.all|first }}"
            "{%% if web.domains.all|slice:\"1:\" %%}"
            "    ServerAlias {{ web.domains.all|slice:\"1:\"|join:' ' }}{%% endif %%}\n"
            "    CustomLog %(logs)s{{ web.primary_domain }} common\n"
            "</VirtualHost>\n" % { 'logs': self.BASE_APACHE_LOGS })
        context = self.get_context(web)
        context.update({ 'conf': template.render(Context({'web': web})) })
        # create system user if not exists
        self.append("id %(username)s || useradd %(username)s \\\n"
                    "  --password '%(password)s' \\\n"
                    "  --shell /dev/null" % context)
        self.append("mkdir -p %(root)s" % context)
        self.append("chown %(username)s.%(username)s %(root)s" % context)
        # create apache conf
        self.append("{ echo -e '%(conf)s' | diff %(sites_available)s - ; } ||"
                    "  { echo -e '%(conf)s' > %(sites_available)s; UPDATED=1; }" % context)
        
        # enable or dissabe this site
        self.append("ls -l %(sites_enabled)s; DISABLED=$?" % context)
        if web.is_active:
            self.append("if [[ $DISABLED ]]; then a2ensite %(name)s;\n"
                        "else UPDATED=0; fi" % context)
        else:
            self.append("if [[ ! $DISABLED ]]; then a2dissite %(name)s;\n"
                        "else UPDATED=0; fi" % context)
    
    def delete(self, web):
        context = self.get_context(web)
        self.append("a2dissite %(name)s && UPDATED=1" % context)
        self.append("rm -fr %(home)s" % context)
        self.append("rm -fr %(sites_available)s" % context)
        # TODO cleanup system user
    
    def commit(self):
        """ reload Apache2 if necessary """
        self.append('[[ $UPDATED == 1 ]] && service apache2 reload')
    
    def get_context(self, web):
        sites_available = os.path.join(self.BASE_APACHE_PATH, 'sites-available')
        sites_enabled = os.path.join(self.BASE_APACHE_PATH, 'sites-enabled')
        return {
            'username': web.user.username,
            'password': web.user.password,
            'root': web.root,
            'name': web.name,
            'sites_enabled': sites_enabled,
            'sites_available': os.path.join(sites_available, web.name),
        }

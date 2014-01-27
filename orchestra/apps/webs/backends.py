import os

from django.utils.translation import ugettext_lazy as _

from orchestra.core.backends import ServiceBackend


class Apache2Backend(ServiceBackend):
    name = 'Apache2'
    verbose_name = _("Apache2")
    models = ['webs.Web']
    
    BASE_APACHE_PATH = '/etc/apache2'
    BASE_APACHE_LOGS = '/var/log/apache2/virtual/'
    
    def save(self, web):
        context = self.get_context(web)
        # create system user if not exists
        self.append("id %(username)s || useradd %(username)s"
                    "  --password %(password)s"
                    "  --home-dir %(home)s --create-home"
                    "  --shell SHELL /dev/null" % context)
        # create apache conf
        self.append("{ echo -e '%(apache_conf)s' | diff %(apache_path)s - ; } ||"
                    "  { echo -e '%(apache_conf)s' > %(apache_path)s; UPDATED=1; }" % context)
        
        # enable or dissabe this site
        self.append("ls -l %(apache_enabled_path)s; DISABLED=$?" % context)
        if web.is_active:
            self.append("if [[ $DISABLED ]]; then a2ensite %(name)s;"
                        "else UPDATED=0; fi" % context)
        else:
            self.append("if [[ ! $DISABLED ]]; then a2dissite %(name)s;"
                        "else UPDATED=0; fi" % context)
    
    def delete(self, web):
        context = self.get_context(web)
        self.append("a2dissite %(name)s && UPDATED=1" % context)
        self.append("rm -fr %(home)s" % context)
        self.append("rm -fr %(apache_conf)s" % context)
        # TODO cleanup system user
    
    def commit(self):
        """ reload Apache2 if necessary """
        self.append('$UPDATED && service apache2 reload')
    
    def get_context(self, web):
        template = Template(
            "<VirtualHost *:{{ web.port }}"
            "    DocumentRoot {{ web.home }}"
            "    ServerName {{ web.primary_domain }}"
            "    ServerAlias {{ web.secondary_domains|join' ' }}"
            "    CustomLog %(logs)s{{ web.primary_domain }} common"
            "</VirtualHost>" % { 'logs': self.BASE_APACHE_LOGS })
        sites_available = os.path.join(self.BASE_APACHE_PATH, 'sites-available')
        sites_enabled = os.path.join(self.BASE_APACHE_PATH, 'sites-enabled')
        return {
            'username': web.user.username,
            'password': web.user.password,
            'home': web.home,
            'name': web.name,
            'sites_enabled': sites_enabled,
            'apache_path': os.path.join('sites_availble', web.name),
            'apache_conf': template.render(Context({'web': web})),
        }

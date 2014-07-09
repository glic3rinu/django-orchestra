import os

from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController

from . import WebAppServiceMixin
from .. import settings


class PHPFPMBackend(WebAppServiceMixin, ServiceController):
    verbose_name = _("PHP-FPM")
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.create_webapp_dir(context)
        self.append(
            "{ echo -e '%(fpm_config)s' | diff -N -I'^\s*;;' %(fpm_path)s - ; } ||"
            "  { echo -e '%(fpm_config)s' > %(fpm_path)s; UPDATEDFPM=1; }" % context
        )
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.delete_webapp_dir(context)
    
    def commit(self):
        super(PHPFPMBackend, self).commit()
        self.append('[[ $UPDATEDFPM == 1 ]] && service php5-fpm reload')
    
    def get_context(self, webapp):
        context = super(PHPFPMBackend, self).get_context(webapp)
        context.update({
            'init_vars': webapp.get_php_init_vars(),
            'fpm_port': webapp.get_fpm_port(),
        })
        context['fpm_listen'] = settings.WEBAPPS_FPM_LISTEN % context
        fpm_config = Template(
            "[{{ user }}]\n"
            ";; {{ banner }}\n"
            "user = {{ user }}\n"
            "group = {{ group }}\n\n"
            "listen = {{ fpm_listen | safe }}\n"
            "listen.owner = {{ user }}\n"
            "listen.group = {{ group }}\n"
            "pm = ondemand\n"
            "pm.max_children = 4\n"
            "{% for name,value in init_vars.iteritems %}"
            "php_admin_value[{{ name | safe }}] = {{ value | safe }}\n"
            "{% endfor %}"
        ) 
        fpm_file = '%(user)s.conf' % context
        context.update({
            'fpm_config': fpm_config.render(Context(context)),
            'fpm_path': os.path.join(settings.WEBAPPS_PHPFPM_POOL_PATH, fpm_file),
        })
        return context


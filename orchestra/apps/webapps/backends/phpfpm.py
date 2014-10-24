import os
import textwrap

from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController

from . import WebAppServiceMixin
from .. import settings


class PHPFPMBackend(WebAppServiceMixin, ServiceController):
    """ Per-webapp php application """
    verbose_name = _("PHP-FPM")
    directive = 'fpm'
    
    def save(self, webapp):
        if not self.valid_directive(webapp):
            return
        context = self.get_context(webapp)
        self.create_webapp_dir(context)
        self.append(textwrap.dedent("""\
            {
                echo -e '%(fpm_config)s' | diff -N -I'^\s*;;' %(fpm_path)s -
            } || {
                echo -e '%(fpm_config)s' > %(fpm_path)s
                UPDATEDFPM=1
            }""" % context))
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.append("rm '%(fpm_config)s'" % context)
        self.delete_webapp_dir(context)
    
    def commit(self):
        super(PHPFPMBackend, self).commit()
        self.append(textwrap.dedent("""
            [[ $UPDATEDFPM == 1 ]] && {
                service php5-fpm start
                service php5-fpm reload
            }"""))
    
    def get_context(self, webapp):
        if not self.valid_directive(webapp):
            return
        context = super(PHPFPMBackend, self).get_context(webapp)
        context.update({
            'init_vars': self.get_php_init_vars(webapp),
            'fpm_port': webapp.get_fpm_port(),
        })
        context['fpm_listen'] = settings.WEBAPPS_FPM_LISTEN % context
        fpm_config = Template(textwrap.dedent("""\
            ;; {{ banner }}
            [{{ user }}]
            user = {{ user }}
            group = {{ group }}
            
            listen = {{ fpm_listen | safe }}
            listen.owner = {{ user }}
            listen.group = {{ group }}
            pm = ondemand
            pm.max_children = 4
            {% for name,value in init_vars.iteritems %}
            php_admin_value[{{ name | safe }}] = {{ value | safe }}{% endfor %}"""
        ))
        context.update({
            'fpm_config': fpm_config.render(Context(context)),
            'fpm_path': settings.WEBAPPS_PHPFPM_POOL_PATH % context,
        })
        return context


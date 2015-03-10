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
    default_route_match = "webapp.type.endswith('-fpm')"
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.create_webapp_dir(context)
        self.set_under_construction(context)
        self.append(textwrap.dedent("""\
            {
                echo -e '%(fpm_config)s' | diff -N -I'^\s*;;' %(fpm_path)s -
            } || {
                echo -e '%(fpm_config)s' > %(fpm_path)s
                UPDATEDFPM=1
            }""") % context
        )
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.append("rm '%(fpm_path)s'" % context)
        self.delete_webapp_dir(context)
    
    def commit(self):
        if not self.cmds:
            return
        super(PHPFPMBackend, self).commit()
        self.append(textwrap.dedent("""
            if [[ $UPDATEDFPM == 1 ]]; then
                service php5-fpm reload
                service php5-fpm start
            fi"""))
    
    def get_fpm_config(self, webapp, context):
        context.update({
            'init_vars': webapp.type_instance.get_php_init_vars(webapp),
            'fpm_port': webapp.get_fpm_port(),
            'max_children': webapp.get_options().get('processes', False),
            'request_terminate_timeout': webapp.get_options().get('timeout', False),
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
            {% if max_children %}pm.max_children = {{ max_children }}{% endif %}
            {% if request_terminate_timeout %}request_terminate_timeout = {{ request_terminate_timeout }}{% endif %}
            {% for name, value in init_vars.iteritems %}
            php_admin_value[{{ name | safe }}] = {{ value | safe }}{% endfor %}
            """
        ))
        return fpm_config.render(Context(context))
    
    def get_context(self, webapp):
        context = super(PHPFPMBackend, self).get_context(webapp)
        context.update({
            'fpm_config': self.get_fpm_config(webapp, context),
            'fpm_path': settings.WEBAPPS_PHPFPM_POOL_PATH % context,
        })
        return context


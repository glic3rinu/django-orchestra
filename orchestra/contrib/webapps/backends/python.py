import os
import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController, replace

from . import WebAppServiceMixin
from .. import settings


class uWSGIPythonController(WebAppServiceMixin, ServiceController):
    """
    <a href="http://uwsgi-docs.readthedocs.org/en/latest/Emperor.html">Emperor mode</a>
    """
    verbose_name = _("Python uWSGI")
    default_route_match = "webapp.type.endswith('python')"
    doc_settings = (settings, (
        'WEBAPPS_UWSGI_BASE_DIR',
        'WEBAPPS_PYTHON_MAX_REQUESTS',
        'WEBAPPS_PYTHON_DEFAULT_MAX_WORKERS',
        'WEBAPPS_PYTHON_DEFAULT_TIMEOUT',
    ))
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.create_webapp_dir(context)
        self.set_under_construction(context)
        self.save_uwsgi(webapp, context)
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.delete_uwsgi(webapp, context)
        self.delete_webapp_dir(context)
    
    def save_uwsgi(self, webapp, context):
        self.append("echo '%(uwsgi_config)s' > %(vassal_path)s" % context)
    
    def delete_uwsgi(self, webapp, context):
        self.append("rm -f %(vassal_path)s" % context)
    
    def get_uwsgi_ini(self, context):
        return textwrap.dedent("""\
            # %(banner)s
            [uwsgi]
            plugins          = python{python_version_number}
            chdir            = {app_path}
            module           = {app_name}.wsgi
            chmod-socket     = 660
            stats            = /run/uwsgi/%(deb-confnamespace)/%(deb-confname)/statsocket
            vacuum           = true
            uid              = {user}
            gid              = {group}
            env              = HOME={home}
            harakiri         = {timeout}
            max-requests     = {max_requests}
            
            cheaper-algo     = spare
            cheaper          = 1
            workers          = {workers}
            cheaper-step     = 1
            cheaper-overload = 5"""
        ).format(context)
    
    def update_uwsgi_context(self, webapp, context):
        context.update({
            'uwsgi_ini': self.get_uwsgi_ini(context),
            'uwsgi_dir': settings.WEBAPPS_UWSGI_BASE_DIR,
            'vassal_path': os.path.join(settings.WEBAPPS_UWSGI_BASE_DIR,
                'vassals/%s' % context['app_name']),
        })
        return context
    
    def get_context(self, webapp):
        context = super(PHPController, self).get_context(webapp)
        options = webapp.get_options()
        context.update({
            'python_version': webapp.type_instance.get_python_version(),
            'python_version_number': webapp.type_instance.get_python_version_number(),
            'max_requests': settings.WEBAPPS_PYTHON_MAX_REQUESTS,
            'workers': options.get('processes', settings.WEBAPPS_PYTHON_DEFAULT_MAX_WORKERS),
            'timeout': options.get('timeout', settings.WEBAPPS_PYTHON_DEFAULT_TIMEOUT),
        })
        self.update_uwsgi_context(webapp, context)
        replace(context, "'", '"')
        return context

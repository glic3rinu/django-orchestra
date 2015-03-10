import os
import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController

from . import WebAppServiceMixin
from .. import settings


class PHPFcgidBackend(WebAppServiceMixin, ServiceController):
    """ Per-webapp fcgid application """
    verbose_name = _("PHP-Fcgid")
    directive = 'fcgid'
    default_route_match = "webapp.type.endswith('-fcgid')"
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.create_webapp_dir(context)
        self.set_under_construction(context)
        self.append("mkdir -p %(wrapper_dir)s" % context)
        self.append(textwrap.dedent("""\
            {
                echo -e '%(wrapper)s' | diff -N -I'^\s*#' %(wrapper_path)s -
            } || {
                echo -e '%(wrapper)s' > %(wrapper_path)s; UPDATED_APACHE=1
            }""") % context
        )
        self.append("chmod +x %(wrapper_path)s" % context)
        self.append("chown -R %(user)s:%(group)s %(wrapper_dir)s" % context)
        if context['cmd_options']:
            self.append(textwrap.dedent("""
                {
                    echo -e '%(cmd_options)s' | diff -N -I'^\s*#' %(cmd_options_path)s -
                } || {
                    echo -e '%(cmd_options)s' > %(cmd_options_path)s; UPDATED_APACHE=1
                }""" ) % context
            )
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.append("rm -f '%(wrapper_path)s'" % context)
        self.append("rm -f '%(cmd_options_path)s'" % context)
        self.delete_webapp_dir(context)
    
    def commit(self):
        self.append('if [[ $UPDATED_APACHE == 1 ]]; then service apache2 reload; fi')
    
    def get_fcgid_wrapper(self, webapp, context):
        opt = webapp.type_instance
        # Format PHP init vars
        init_vars = opt.get_php_init_vars(webapp)
        if init_vars:
            init_vars = [ '-d %s="%s"' % (k,v) for k,v in init_vars.iteritems() ]
        init_vars = ', '.join(init_vars)
        
        context.update({
            'php_binary': opt.php_binary,
            'php_rc': opt.php_rc,
            'php_init_vars': init_vars,
        })
        return textwrap.dedent("""\
            #!/bin/sh
            # %(banner)s
            export PHPRC=%(php_rc)s
            exec %(php_binary)s %(php_init_vars)s""") % context
    
    def get_fcgid_cmd_options(self, webapp, context):
        maps = {
            'MaxProcesses': webapp.get_options().get('processes', None),
            'IOTimeout': webapp.get_options().get('timeout', None),
        }
        cmd_options = []
        for directive, value in maps.iteritems():
            if value:
                cmd_options.append("%s %s" % (directive, value))
        if cmd_options:
            head = '# %(banner)s\nFcgidCmdOptions %(wrapper_path)s' % context
            cmd_options.insert(0, head)
            return ' \\\n    '.join(cmd_options)
    
    def get_context(self, webapp):
        context = super(PHPFcgidBackend, self).get_context(webapp)
        wrapper_path = settings.WEBAPPS_FCGID_PATH % context
        context.update({
            'wrapper': self.get_fcgid_wrapper(webapp, context),
            'wrapper_path': wrapper_path,
            'wrapper_dir': os.path.dirname(wrapper_path),
        })
        context.update({
            'cmd_options': self.get_fcgid_cmd_options(webapp, context),
            'cmd_options_path': settings.WEBAPPS_FCGID_CMD_OPTIONS_PATH % context,
        })
        return context

import os
import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController

from . import WebAppServiceMixin
from .. import settings


class PHPFcgidBackend(WebAppServiceMixin, ServiceController):
    """ Per-webapp fcgid application """
    verbose_name = _("PHP-Fcgid")
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.create_webapp_dir(context)
        self.append("mkdir -p %(wrapper_dir)s" % context)
        self.append(textwrap.dedent("""\
            {
                echo -e '%(wrapper_content)s' | diff -N -I'^\s*#' %(wrapper_path)s -
            } || {
                echo -e '%(wrapper_content)s' > %(wrapper_path)s; UPDATED_APACHE=1
            }""" % context))
        self.append("chmod +x %(wrapper_path)s" % context)
        self.append("chown -R %(user)s.%(group)s %(wrapper_dir)s" % context)
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.append("rm '%(wrapper_path)s'" % context)
        self.delete_webapp_dir(context)
    
    def commit(self):
        super(PHPFcgidBackend, self).commit()
        self.append("[[ $UPDATED_APACHE == 1 ]] && { service apache2 reload; }")
    
    def get_context(self, webapp):
        context = super(PHPFcgidBackend, self).get_context(webapp)
        init_vars = self.get_php_init_vars(webapp)
        if init_vars:
            init_vars = [ '%s="%s"' % (k,v) for v,k in init_vars.iteritems() ]
            init_vars = ', -d '.join(init_vars)
            context['init_vars'] = '-d %s' % init_vars
        else:
            context['init_vars'] = ''
        wrapper_path = settings.WEBAPPS_FCGID_PATH % context
        context.update({
            'wrapper_content': textwrap.dedent("""\
                #!/bin/sh
                # %(banner)s
                export PHPRC=/etc/%(type)s/cgi/
                exec /usr/bin/%(type)s-cgi %(init_vars)s""" % context),
            'wrapper_path': wrapper_path,
            'wrapper_dir': os.path.dirname(wrapper_path),
        })
        return context

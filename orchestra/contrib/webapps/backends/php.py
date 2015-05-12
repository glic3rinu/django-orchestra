import os
import textwrap
from collections import OrderedDict

from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController, replace

from . import WebAppServiceMixin
from .. import settings


class PHPBackend(WebAppServiceMixin, ServiceController):
    """
    PHP support for apache-mod-fcgid and php-fpm.
    It handles switching between these two PHP process management systemes.
    """
    MERGE = settings.WEBAPPS_MERGE_PHP_WEBAPPS
    
    verbose_name = _("PHP FPM/FCGID")
    default_route_match = "webapp.type.endswith('php')"
    doc_settings = (settings, (
        'WEBAPPS_MERGE_PHP_WEBAPPS',
        'WEBAPPS_FPM_DEFAULT_MAX_CHILDREN',
        'WEBAPPS_PHP_CGI_BINARY_PATH',
        'WEBAPPS_PHP_CGI_RC_DIR',
        'WEBAPPS_PHP_CGI_INI_SCAN_DIR',
        'WEBAPPS_FCGID_CMD_OPTIONS_PATH',
        'WEBAPPS_PHPFPM_POOL_PATH',
        'WEBAPPS_PHP_MAX_REQUESTS',
    ))
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.create_webapp_dir(context)
        if webapp.type_instance.is_fpm:
            self.save_fpm(webapp, context)
            self.delete_fcgid(webapp, context)
        elif webapp.type_instance.is_fcgid:
            self.save_fcgid(webapp, context)
            self.delete_fpm(webapp, context)
        self.set_under_construction(context)
    
    def save_fpm(self, webapp, context):
        self.append(textwrap.dedent("""\
            fpm_config='%(fpm_config)s'
            {
                echo -e "${fpm_config}" | diff -N -I'^\s*;;' %(fpm_path)s -
            } || {
                echo -e "${fpm_config}" > %(fpm_path)s
                UPDATED_FPM=1
            }
            """) % context
        )
    
    def save_fcgid(self, webapp, context):
        self.append("mkdir -p %(wrapper_dir)s" % context)
        self.append(textwrap.dedent("""\
            wrapper='%(wrapper)s'
            {
                echo -e "${wrapper}" | diff -N -I'^\s*#' %(wrapper_path)s -
            } || {
                echo -e "${wrapper}" > %(wrapper_path)s
                if [[ %(is_mounted)i -eq 1 ]]; then
                    # Reload fcgid wrapper
                    pkill -SIGHUP -U %(user)s "^%(php_binary)s$" || true
                fi
            }
            """) % context
        )
        self.append("chmod 550 %(wrapper_dir)s" % context)
        self.append("chmod 550 %(wrapper_path)s" % context)
        self.append("chown -R %(user)s:%(group)s %(wrapper_dir)s" % context)
        if context['cmd_options']:
            self.append(textwrap.dedent("""
                cmd_options='%(cmd_options)s'
                {
                    echo -e "${cmd_options}" | diff -N -I'^\s*#' %(cmd_options_path)s -
                } || {
                    echo -e "${cmd_options}" > %(cmd_options_path)s
                    [[ ${UPDATED_APACHE} -eq 0 ]] && UPDATED_APACHE=%(is_mounted)i
                }
                """ ) % context
            )
        else:
            self.append("rm -f %(cmd_options_path)s" % context)
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        if webapp.type_instance.is_fpm:
            self.delete_fpm(webapp, context)
        elif webapp.type_instance.is_fcgid:
            self.delete_fcgid(webapp, context)
        self.delete_webapp_dir(context)
    
    def delete_fpm(self, webapp, context):
        # Better not delete a pool used by other apps
        if not self.MERGE:
            self.append("rm -f %(fpm_path)s" % context)
    
    def delete_fcgid(self, webapp, context):
        # Better not delete a wrapper used by other apps
        if not self.MERGE:
            self.append("rm -f %(wrapper_path)s" % context)
            self.append("rm -f %(cmd_options_path)s" % context)
    
    def prepare(self):
        super(PHPBackend, self).prepare()
        # Coordinate apache restart with php backend in order not to overdo it
        self.append(textwrap.dedent("""\
            backend="PHPBackend"
            echo "$backend" >> /dev/shm/restart.apache2
            """)
        )
    
    def commit(self):
        self.append(textwrap.dedent("""
            if [[ $UPDATED_FPM -eq 1 ]]; then
                service php5-fpm reload
            fi
            
            # Coordinate Apache restart with other concurrent backends (i.e. Apache2Backend)
            is_last=0
            mv /dev/shm/restart.apache2 /dev/shm/restart.apache2.locked || {
                sleep 0.2
                mv /dev/shm/restart.apache2 /dev/shm/restart.apache2.locked
            }
            state="$(grep -v "$backend" /dev/shm/restart.apache2.locked)" || is_last=1
            [[ $is_last -eq 0 ]] && {
                echo "$state" | grep -v ' RESTART$' || is_last=1
            }
            if [[ $is_last -eq 1 ]]; then
                if [[ $UPDATED_APACHE -eq 1 || "$state" =~ .*RESTART$ ]]; then
                    service apache2 status && service apache2 reload || service apache2 start
                fi
                rm /dev/shm/restart.apache2.locked
            else
                echo -n "$state" > /dev/shm/restart.apache2.locked
                if [[ $UPDATED_APACHE -eq 1 ]]; then
                    echo "$backend RESTART" >> /dev/shm/restart.apache2.locked
                fi
                mv /dev/shm/restart.apache2.locked /dev/shm/restart.apache2
            fi
            # End of coordination
            """)
        )
        super(PHPBackend, self).commit()
    
    def get_options(self, webapp):
        kwargs = {}
        if self.MERGE:
            kwargs = {
                'webapp__account': webapp.account,
                'webapp__type': webapp.type,
                'webapp__data__contains': '"php_version":"%s"' % webapp.data['php_version'],
            }
        return webapp.get_options(**kwargs)
    
    def get_fpm_config(self, webapp, context):
        options = self.get_options(webapp)
        context.update({
            'init_vars': webapp.type_instance.get_php_init_vars(merge=self.MERGE),
            'max_children': options.get('processes', settings.WEBAPPS_FPM_DEFAULT_MAX_CHILDREN),
            'request_terminate_timeout': options.get('timeout', False),
        })
        context['fpm_listen'] = webapp.type_instance.FPM_LISTEN % context
        fpm_config = Template(textwrap.dedent("""\
            ;; {{ banner }}
            [{{ user }}]
            user = {{ user }}
            group = {{ group }}
            
            listen = {{ fpm_listen | safe }}
            listen.owner = {{ user }}
            listen.group = {{ group }}
            pm = ondemand
            pm.max_requests = {{ max_requests }}
            pm.max_children = {{ max_children }}
            {% if request_terminate_timeout %}request_terminate_timeout = {{ request_terminate_timeout }}{% endif %}
            {% for name, value in init_vars.items %}
            php_admin_value[{{ name | safe }}] = {{ value | safe }}{% endfor %}
            """
        ))
        return fpm_config.render(Context(context))
    
    def get_fcgid_wrapper(self, webapp, context):
        opt = webapp.type_instance
        # Format PHP init vars
        init_vars = opt.get_php_init_vars(merge=self.MERGE)
        if init_vars:
            init_vars = [ "-d %s='%s'" % (k, v.replace("'", '"')) for k,v in init_vars.items() ]
        init_vars = ' \\\n    '.join(init_vars)
        context.update({
            'php_binary_path': os.path.normpath(settings.WEBAPPS_PHP_CGI_BINARY_PATH % context),
            'php_rc': os.path.normpath(settings.WEBAPPS_PHP_CGI_RC_DIR % context),
            'php_ini_scan': os.path.normpath(settings.WEBAPPS_PHP_CGI_INI_SCAN_DIR % context),
            'php_init_vars': init_vars,
        })
        context['php_binary'] = os.path.basename(context['php_binary_path'])
        return textwrap.dedent("""\
            #!/bin/sh
            # %(banner)s
            export PHPRC=%(php_rc)s
            export PHP_INI_SCAN_DIR=%(php_ini_scan)s
            export PHP_FCGI_MAX_REQUESTS=%(max_requests)s
            exec %(php_binary_path)s %(php_init_vars)s""") % context
    
    def get_fcgid_cmd_options(self, webapp, context):
        options = self.get_options(webapp)
        maps = OrderedDict(
            MaxProcesses=options.get('processes', None),
            IOTimeout=options.get('timeout', None),
        )
        cmd_options = []
        for directive, value in maps.items():
            if value:
                cmd_options.append(
                    "%s %s" % (directive, value.replace("'", '"'))
                )
        if cmd_options:
            head = (
                '# %(banner)s\n'
                'FcgidCmdOptions %(wrapper_path)s'
            ) % context
            cmd_options.insert(0, head)
            return ' \\\n    '.join(cmd_options)
    
    def update_fcgid_context(self, webapp, context):
        wrapper_path = webapp.type_instance.FCGID_WRAPPER_PATH % context
        context.update({
            'wrapper': self.get_fcgid_wrapper(webapp, context),
            'wrapper_path': wrapper_path,
            'wrapper_dir': os.path.dirname(wrapper_path),
        })
        replace(context, "'", '"')
        context.update({
            'cmd_options': self.get_fcgid_cmd_options(webapp, context),
            'cmd_options_path': settings.WEBAPPS_FCGID_CMD_OPTIONS_PATH % context,
        })
        return context
    
    def update_fpm_context(self, webapp, context):
        context.update({
            'fpm_config': self.get_fpm_config(webapp, context),
            'fpm_path': settings.WEBAPPS_PHPFPM_POOL_PATH % context,
        })
        return context
    
    def get_context(self, webapp):
        context = super(PHPBackend, self).get_context(webapp)
        context.update({
            'php_version': webapp.type_instance.get_php_version(),
            'php_version_number': webapp.type_instance.get_php_version_number(),
            'max_requests': settings.WEBAPPS_PHP_MAX_REQUESTS,
        })
        self.update_fpm_context(webapp, context)
        # Fcgid context do contain special charactes
        replace(context, "'", '"')
        self.update_fcgid_context(webapp, context)
        return context

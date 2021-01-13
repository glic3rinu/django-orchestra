import os
import textwrap
from collections import OrderedDict

from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController

from . import WebAppServiceMixin
from .. import settings, utils


class PHPController(WebAppServiceMixin, ServiceController):
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
        self.delete_old_config(webapp)
        context = self.get_context(webapp)
        self.create_webapp_dir(context)
        if webapp.type_instance.is_fpm:
            self.save_fpm(webapp, context)
        elif webapp.type_instance.is_fcgid:
            self.save_fcgid(webapp, context)
        else:
            raise TypeError("Unknown PHP execution type")
#        LEGACY CLEANUP FUNCTIONS. TODO REMOVE WHEN SURE NOT NEEDED.
#        self.delete_fcgid(webapp, context, preserve=True)
#        self.delete_fpm(webapp, context, preserve=True)
        self.set_under_construction(context)

    def delete_config(self,webapp):
        context = self.get_context(webapp)
        to_delete = []
        if webapp.type_instance.is_fpm:
            to_delete.append(settings.WEBAPPS_PHPFPM_POOL_PATH % context)
            to_delete.append(settings.WEBAPPS_FPM_LISTEN % context)
        elif webapp.type_instance.is_fcgid:
            to_delete.append(settings.WEBAPPS_FCGID_WRAPPER_PATH % context)
            to_delete.append(settings.WEBAPPS_FCGID_CMD_OPTIONS_PATH % context)
        for item in to_delete:
            self.append('rm -f "{}"'.format(item))

    def delete_old_config(self,webapp):
        # Check if we loaded the old version of the webapp. If so, we're updating
        # rather than creating, so we must make sure the old config files are removed.
        if hasattr(webapp, '_old_self'):
            self.append("# Clean old configuration files")
            self.delete_config(webapp._old_self)
        else:
            self.append("# No old config files to delete")

    def save_fpm(self, webapp, context):
        self.append(textwrap.dedent("""
            # Generate FPM configuration
            read -r -d '' fpm_config << 'EOF' || true
            %(fpm_config)s
            EOF
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
        self.append(textwrap.dedent("""
            # Generate FCGID configuration
            read -r -d '' wrapper << 'EOF' || true
            %(wrapper)s
            EOF
            {
                echo -e "${wrapper}" | diff -N -I'^\s*#' %(wrapper_path)s -
            } || {
                echo -e "${wrapper}" > %(wrapper_path)s
                if [[ %(is_mounted)i -eq 1 ]]; then
                    # Reload fcgid wrapper (All PHP versions, because of version changing support)
                    pkill -SIGHUP -U %(user)s "^php[0-9\.]+-cgi$" || true
                fi
            }
            chmod 550 %(wrapper_dir)s
            chmod 550 %(wrapper_path)s
            chown -R %(user)s:%(group)s %(wrapper_dir)s""") % context
        )
        if context['cmd_options']:
            self.append(textwrap.dedent("""\
                # FCGID options
                read -r -d '' cmd_options << 'EOF' || true
                %(cmd_options)s
                EOF
                {
                    echo -e "${cmd_options}" | diff -N -I'^\s*#' %(cmd_options_path)s -
                } || {
                    echo -e "${cmd_options}" > %(cmd_options_path)s
                    [[ ${UPDATED_APACHE} -eq 0 ]] && UPDATED_APACHE=%(is_mounted)i
                }
                """ ) % context
            )
        else:
            self.append("rm -f %(cmd_options_path)s\n" % context)
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.delete_old_config(webapp)
#        if webapp.type_instance.is_fpm:
#            self.delete_fpm(webapp, context)
#        elif webapp.type_instance.is_fcgid:
#            self.delete_fcgid(webapp, context)
        self.delete_webapp_dir(context)
    
    def has_sibilings(self, webapp, context):
        return type(webapp).objects.filter(
            account=webapp.account_id,
            data__contains='"php_version":"%s"' % context['php_version'],
        ).exclude(id=webapp.pk).exists()
    
    def all_versions_to_delete(self, webapp, context, preserve=False):
        context_copy = dict(context)
        for php_version, verbose in settings.WEBAPPS_PHP_VERSIONS:
            if preserve and php_version == context['php_version']:
                continue
            php_version_number = utils.extract_version_number(php_version)
            context_copy['php_version'] = php_version
            context_copy['php_version_number'] = php_version_number
            if not self.MERGE or not self.has_sibilings(webapp, context_copy):
                yield context_copy
    
    def delete_fpm(self, webapp, context, preserve=False):
        """ delete all pools in order to efectively support changing php-fpm version """
        for context_copy in self.all_versions_to_delete(webapp, context, preserve):
            context_copy['fpm_path'] = settings.WEBAPPS_PHPFPM_POOL_PATH % context_copy
            self.append("rm -f %(fpm_path)s" % context_copy)
    
    def delete_fcgid(self, webapp, context, preserve=False):
        """ delete all pools in order to efectively support changing php-fcgid version """
        for context_copy in self.all_versions_to_delete(webapp, context, preserve):
            context_copy.update({
                'wrapper_path': settings.WEBAPPS_FCGID_WRAPPER_PATH % context_copy,
                'cmd_options_path': settings.WEBAPPS_FCGID_CMD_OPTIONS_PATH % context_copy,
            })
            self.append("rm -f %(wrapper_path)s" % context_copy)
            self.append("rm -f %(cmd_options_path)s" % context_copy)
    
    def prepare(self):
        super(PHPController, self).prepare()
        self.append(textwrap.dedent("""
            BACKEND="PHPController"
            echo "$BACKEND" >> /dev/shm/reload.apache2
            
            function coordinate_apache_reload () {
                # Coordinate Apache reload with other concurrent backends (e.g. Apache2Controller)
                is_last=0
                counter=0
                while ! mv /dev/shm/reload.apache2 /dev/shm/reload.apache2.locked; do
                    sleep 0.1;
                    if [[ $counter -gt 4 ]]; then
                        echo "[ERROR]: Apache reload synchronization deadlocked!" >&2
                        exit 10
                    fi
                    counter=$(($counter+1))
                done
                state="$(grep -v -E "^$BACKEND($|\s)" /dev/shm/reload.apache2.locked)" || is_last=1
                [[ $is_last -eq 0 ]] && {
                    echo "$state" | grep -v ' RELOAD$' || is_last=1
                }
                if [[ $is_last -eq 1 ]]; then
                    echo "[DEBUG]: Last backend to run, update: $UPDATED_APACHE, state: '$state'"
                    if [[ $UPDATED_APACHE -eq 1 || "$state" =~ .*RELOAD$ ]]; then
                        if service apache2 status > /dev/null; then
                            service apache2 reload
                        else
                            service apache2 start
                        fi
                    fi
                    rm /dev/shm/reload.apache2.locked
                else
                    echo "$state" > /dev/shm/reload.apache2.locked
                    if [[ $UPDATED_APACHE -eq 1 ]]; then
                        echo -e "[DEBUG]: Apache will be reloaded by another backend:\\n${state}"
                        echo "$BACKEND RELOAD" >> /dev/shm/reload.apache2.locked
                    fi
                    mv /dev/shm/reload.apache2.locked /dev/shm/reload.apache2
                fi
            }""")
        )
    
    def commit(self):
        context = {
            'reload_pool': settings.WEBAPPS_PHPFPM_RELOAD_POOL,
        }
        self.append(textwrap.dedent("""
            # Apply changes if needed
            if [[ $UPDATED_FPM -eq 1 ]]; then
                %(reload_pool)s
            fi
            coordinate_apache_reload
            """) % context
        )
        super(PHPController, self).commit()
    
    def get_fpm_config(self, webapp, context):
        options = webapp.type_instance.get_options()
        context.update({
            'init_vars': webapp.type_instance.get_php_init_vars(merge=self.MERGE),
            'max_children': options.get('processes', settings.WEBAPPS_FPM_DEFAULT_MAX_CHILDREN),
            'request_terminate_timeout': options.get('timeout', False),
        })
        context['fpm_listen'] = webapp.type_instance.FPM_LISTEN % context
        fpm_config = Template(textwrap.dedent("""\
            ;; {{ banner }}
            [{{ user }}-{{app_name}}]
            user = {{ user }}
            group = {{ group }}
            
            listen = {{ fpm_listen | safe }}
            listen.owner = {{ user }}
            listen.group = {{ group }}
            
            pm = ondemand
            pm.max_requests = {{ max_requests }}
            pm.max_children = {{ max_children }}
            {% if request_terminate_timeout %}
            request_terminate_timeout = {{ request_terminate_timeout }}{% endif %}
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
            init_vars = [ " \\\n    -d %s='%s'" % (k, v.replace("'", '"')) for k,v in init_vars.items() ]
        init_vars = ''.join(init_vars)
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
            exec %(php_binary_path)s%(php_init_vars)s""") % context
    
    def get_fcgid_cmd_options(self, webapp, context):
        options = webapp.type_instance.get_options()
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
        wrapper_path = settings.WEBAPPS_FCGID_WRAPPER_PATH % context
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
    
    def update_fpm_context(self, webapp, context):
        context.update({
            'fpm_config': self.get_fpm_config(webapp, context),
            'fpm_path': settings.WEBAPPS_PHPFPM_POOL_PATH % context,
        })
        return context
    
    def get_context(self, webapp):
        context = super().get_context(webapp)
        context.update({
            'max_requests': settings.WEBAPPS_PHP_MAX_REQUESTS,
        })
        self.update_fpm_context(webapp, context)
        self.update_fcgid_context(webapp, context)
        return context

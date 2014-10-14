import pkgutil
import textwrap


class WebAppServiceMixin(object):
    model = 'webapps.WebApp'
    
    def create_webapp_dir(self, context):
        self.append(textwrap.dedent("""
            path=""
            for dir in $(echo %(app_path)s | tr "/" "\n"); do
                path="${path}/${dir}"
                [ -d $path ] || {
                    mkdir "${path}"
                    chown %(user)s.%(group)s "${path}"
                }
            done
        """ % context))
    
    def get_php_init_vars(self, webapp, per_account=False):
        """
        process php options for inclusion on php.ini
        per_account=True merges all (account, webapp.type) options
        """
        init_vars = []
        options = webapp.options.all()
        if per_account:
            options = webapp.account.webapps.filter(webapp_type=webapp.type)
        for opt in options:
            name = opt.name.replace('PHP-', '')
            value = "%s" % opt.value
            init_vars.append((name, value))
        enabled_functions = []
        for value in options.filter(name='enabled_functions').values_list('value', flat=True):
            enabled_functions += enabled_functions.get().value.split(',')
        if enabled_functions:
            disabled_functions = []
            for function in settings.WEBAPPS_PHP_DISABLED_FUNCTIONS:
                if function not in enabled_functions:
                    disabled_functions.append(function)
            init_vars.append(('dissabled_functions', ','.join(disabled_functions)))
        return init_vars
    
    def delete_webapp_dir(self, context):
        self.append("rm -fr %(app_path)s" % context)
    
    def get_context(self, webapp):
        return {
            'user': webapp.account.username,
            'group': webapp.account.username,
            'app_name': webapp.name,
            'type': webapp.type,
            'app_path': webapp.get_path().rstrip('/'),
            'banner': self.get_banner(),
        }



for __, module_name, __ in pkgutil.walk_packages(__path__):
    # sorry for the exec(), but Import module function fails :(
    exec('from . import %s' % module_name)

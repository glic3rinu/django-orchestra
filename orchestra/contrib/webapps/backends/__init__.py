import pkgutil
import textwrap

from orchestra.contrib.orchestration.backends import replace

from .. import settings


class WebAppServiceMixin(object):
    model = 'webapps.WebApp'
    directive = None
    
    def create_webapp_dir(self, context):
        self.append(textwrap.dedent("""\
            CREATED=0
            [[ ! -e %(app_path)s ]] && CREATED=1
            mkdir -p %(app_path)s
            chown %(user)s:%(group)s %(app_path)s
            """) % context
        )
    
    def set_under_construction(self, context):
        if context['under_construction_path']:
            self.append(textwrap.dedent("""\
                if [[ $CREATED == 1 ]]; then
                    cp -r %(under_construction_path)s %(app_path)s
                    chown -R %(user)s:%(group)s %(app_path)s
                fi""") % context
            )
    
    def delete_webapp_dir(self, context):
        self.append("rm -fr %(app_path)s" % context)
    
    def get_context(self, webapp):
        context = {
            'user': webapp.get_username(),
            'group': webapp.get_groupname(),
            'app_name': webapp.name,
            'type': webapp.type,
            'app_path': webapp.get_path().rstrip('/'),
            'banner': self.get_banner(),
            'under_construction_path': settings.settings.WEBAPPS_UNDER_CONSTRUCTION_PATH,
            'is_mounted': webapp.content_set.exists(),
        }
        replace(context, "'", '"')


for __, module_name, __ in pkgutil.walk_packages(__path__):
    # sorry for the exec(), but Import module function fails :(
    exec('from . import %s' % module_name)

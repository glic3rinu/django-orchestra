import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController

from .. import settings

from . import WebAppServiceMixin


class WordPressBackend(WebAppServiceMixin, ServiceController):
    verbose_name = _("Wordpress")
    model = 'webapps.WebApp'
    default_route_match = "webapp.type == 'wordpress'"
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.create_webapp_dir(context)
        self.append(textwrap.dedent("""\
            # Check if directory is empty befor doing anything
            if [[ ! $(ls -A %(app_path)s) ]]; then
                wget http://wordpress.org/latest.tar.gz -O - --no-check-certificate \\
                    | tar -xzvf - -C %(app_path)s --strip-components=1
                cp %(app_path)s/wp-config-sample.php %(app_path)s/wp-config.php
                sed -i "s/database_name_here/%(db_name)s/" %(app_path)s/wp-config.php
                sed -i "s/username_here/%(db_user)s/" %(app_path)s/wp-config.php
                sed -i "s/password_here/%(db_pass)s/" %(app_path)s/wp-config.php
                sed -i "s/localhost/%(db_host)s/" %(app_path)s/wp-config.php
                mkdir %(app_path)s/wp-content/uploads
                chmod 750 %(app_path)s/wp-content/uploads
                chown -R %(user)s:%(group)s %(app_path)s
            fi""") % context
        )
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.delete_webapp_dir(context)
    
    def get_context(self, webapp):
        context = super(WordPressBackend, self).get_context(webapp)
        context.update({
            'db_name': webapp.data['db_name'],
            'db_user': webapp.data['db_user'],
            'db_pass': webapp.data['db_pass'],
            'db_host': settings.WEBAPPS_DEFAULT_MYSQL_DATABASE_HOST,
        })
        return context

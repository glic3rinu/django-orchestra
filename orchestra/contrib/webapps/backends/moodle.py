import os
import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController, replace

from .. import settings

from . import WebAppServiceMixin


class MoodleController(WebAppServiceMixin, ServiceController):
    """
    Installs the latest version of Moodle available on download.moodle.org
    """
    verbose_name = _("Moodle")
    model = 'webapps.WebApp'
    default_route_match = "webapp.type == 'moodle-php'"
    doc_settings = (settings,
        ('WEBAPPS_DEFAULT_MYSQL_DATABASE_HOST',)
    )
    
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.append(textwrap.dedent("""\
            if [[ $(ls "%(app_path)s" | wc -l) -gt 1 ]]; then
                echo "App directory not empty." 2> /dev/null
                exit 0
            fi
            mkdir -p %(app_path)s
            # Prevent other backends from writting here
            touch %(app_path)s/.lock
            # Weekly caching
            moodle_date=$(date -r $(readlink %(cms_cache_dir)s/moodle) +%%s || echo 0)
            if [[ $moodle_date -lt $(($(date +%%s)-7*24*60*60)) ]]; then
                moodle_url=$(wget https://download.moodle.org/releases/latest/ -O - -q \\
                    | tr ' ' '\\n' \\
                    | grep 'moodle-latest.*.tgz"' \\
                    | sed -E 's#href="([^"]+)".*#\\1#' \\
                    | head -n 1 \\
                    | sed "s#download.php/#download.php/direct/#")
                filename=${moodle_url##*/}
                wget $moodle_url -O - --no-check-certificate \\
                    | tee %(cms_cache_dir)s/$filename \\
                    | tar -xzvf - -C %(app_path)s --strip-components=1
                rm -f %(cms_cache_dir)s/moodle
                ln -s %(cms_cache_dir)s/$filename %(cms_cache_dir)s/moodle
            else
                tar -xzvf %(cms_cache_dir)s/moodle -C %(app_path)s --strip-components=1
            fi
            mkdir %(app_path)s/moodledata && {
                chmod 750 %(app_path)s/moodledata
                echo -n 'order deny,allow\\ndeny from all' >  %(app_path)s/moodledata/.htaccess
            }
            if [[ ! -e %(app_path)s/config.php ]]; then
                cp %(app_path)s/config-dist.php %(app_path)s/config.php
                sed -i "s#dbtype\s*= '.*#dbtype    = '%(db_type)s';#" %(app_path)s/config.php
                sed -i "s#dbhost\s*= '.*#dbhost    = '%(db_host)s';#" %(app_path)s/config.php
                sed -i "s#dbname\s*= '.*#dbname    = '%(db_name)s';#" %(app_path)s/config.php
                sed -i "s#dbuser\s*= '.*#dbuser    = '%(db_user)s';#" %(app_path)s/config.php
                sed -i "s#dbpass\s*= '.*#dbpass    = '%(password)s';#" %(app_path)s/config.php
                sed -i "s#dataroot\s*= '.*#dataroot    = '%(app_path)s/moodledata';#" %(app_path)s/config.php
                sed -i "s#wwwroot\s*= '.*#wwwroot    = '%(www_root)s';#" %(app_path)s/config.php
                
            fi
            rm %(app_path)s/.lock
            chown -R %(user)s:%(group)s %(app_path)s
            # Run install moodle cli command on the background, because it takes so long...
            stdout=$(mktemp)
            stderr=$(mktemp)
            nohup su - %(user)s --shell /bin/bash << 'EOF' > $stdout 2> $stderr &
                php %(app_path)s/admin/cli/install_database.php \\
                    --fullname="%(site_name)s" \\
                    --shortname="%(site_name)s" \\
                    --adminpass="%(password)s" \\
                    --adminemail="%(email)s" \\
                    --non-interactive \\
                    --agree-license \\
                    --allow-unstable
            EOF
            pid=$!
            sleep 2
            if ! ps -p $pid > /dev/null; then
                cat $stdout
                cat $stderr >&2
                exit_code=$(wait $pid)
            fi
            rm $stdout $stderr
            """) % context
        )
    
    def get_context(self, webapp):
        context = super(MoodleController, self).get_context(webapp)
        contents = webapp.content_set.all()
        context.update({
            'db_type': 'mysqli',
            'db_name': webapp.data['db_name'],
            'db_user': webapp.data['db_user'],
            'password': webapp.data['password'],
            'db_host': settings.WEBAPPS_DEFAULT_MYSQL_DATABASE_HOST,
            'email': webapp.account.email,
            'site_name': "%s Courses" % webapp.account.get_full_name(),
            'cms_cache_dir': os.path.normpath(settings.WEBAPPS_CMS_CACHE_DIR),
            'www_root': contents[0].website.get_absolute_url() if contents else 'http://empty'
        })
        return replace(context, '"', "'")

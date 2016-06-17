import textwrap
from urllib.parse import urlparse

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController

from .. import settings


class MoodleMuController(ServiceController):
    """
    Creates a Moodle site on a Moodle multisite installation
    
    // config.php
    // map custom domains to sites
    $site_map = array(
        // "<HTTP_HOST>" => ["<SITE_NAME>", "<WWWROOT>"],
    );
    
    $site = getenv("SITE");
    if ( $site == '' ) {
        $http_host = $_SERVER['HTTP_HOST'];
        if (array_key_exists($http_host, $site_map)) {
            $site = $site_map[$http_host][0];
            $wwwroot = $site_map[$http_host][1];
        } elseif (strpos($http_host, '-courses.') !== false) {
            $site = array_shift((explode("-courses.", $http_host)));
            $wwwroot = "https://{$site}-courses.pangea.org";
        } else {
            $site = array_shift((explode(".", $http_host)));
            $wwwroot = "https://{$site}-courses.pangea.org";
        }
    } else {
        $wwwroot = "https://{$site}-courses.pangea.org";
        foreach ($site_map as $key => $value) {
            if ($value[0] == $site) {
                $wwwroot = $value[1];
                break;
            }
        }
    }
    
    $prefix = str_replace('-', '_', $site);
    $CFG->prefix    = "${prefix}_";
    $CFG->wwwroot   = $wwwroot;
    $CFG->dataroot  = "/home/pangea/moodledata/{$site}/";
    """
    verbose_name = _("Moodle multisite")
    model = 'saas.SaaS'
    default_route_match = "saas.service == 'moodle'"
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.delete_site_map(context)
        if context['custom_url']:
            self.insert_site_map(context)
        self.append(textwrap.dedent("""\
            mkdir -p %(moodledata_path)s
            chown %(user)s:%(user)s %(moodledata_path)s
            export SITE=%(site_name)s
            CHANGE_PASSWORD=0
            # TODO su moodle user
            php %(moodle_path)s/admin/cli/install_database.php \\
                --fullname="%(site_name)s" \\
                --shortname="%(site_name)s" \\
                --adminpass="%(password)s" \\
                --adminemail="%(email)s" \\
                --non-interactive \\
                --agree-license \\
                --allow-unstable || CHANGE_PASSWORD=1
            """) % context
        )
        if context['password']:
            self.append(textwrap.dedent("""\
                mysql \\
                    --host="%(db_host)s" \\
                    --user="%(db_user)s" \\
                    --password="%(db_pass)s" \\
                    --execute='UPDATE %(db_prefix)s_user
                               SET password=MD5("%(password)s")
                               WHERE username="admin";' \\
                    %(db_name)s
            """) % context
        )
        if context['crontab']:
            context['escaped_crontab'] = context['crontab'].replace('$', '\\$')
            self.append(textwrap.dedent("""\
                # Configuring Moodle crontabs
                if ! crontab -u %(user)s -l | grep 'Moodle:"%(site_name)s"' > /dev/null; then
                cat << EOF | su - %(user)s --shell /bin/bash -c 'crontab'
                $(crontab -u %(user)s -l)
                
                # %(banner)s - Moodle:"%(site_name)s"
                %(escaped_crontab)s
                EOF
                fi""") % context
            )
    
    def delete_site_map(self, context):
        self.append(textwrap.dedent("""\
            sed -i '/^\s*"[^\s]*"\s*=>\s*\["%(site_name)s",\s*".*/d' %(moodle_path)s/config.php
            """) % context
        )
    
    def insert_site_map(self, context):
        self.append(textwrap.dedent("""\
            regex='\s*\$site_map\s+=\s+array\('
            newline='    "%(custom_domain)s" => ["%(site_name)s", "%(custom_url)s"],  // %(banner)s'
            sed -i -r "s#$regex#\$site_map = array(\\n$newline#" %(moodle_path)s/config.php
            """) % context
        )
    
    def delete(self, saas):
        context = self.get_context(saas)
        self.append(textwrap.dedent("""
            rm -rf %(moodledata_path)s
            # Delete tables with prefix %(db_prefix)s
            mysql -Nrs \\
                --host="%(db_host)s" \\
                --user="%(db_user)s" \\
                --password="%(db_pass)s" \\
                --execute='SET GROUP_CONCAT_MAX_LEN=10000;
                           SET @tbls = (SELECT GROUP_CONCAT(TABLE_NAME)
                                        FROM information_schema.TABLES
                                        WHERE TABLE_SCHEMA = "%(db_name)s"
                                        AND TABLE_NAME LIKE "%(db_prefix)s_%%");
                           SET @delStmt = CONCAT("DROP TABLE ",  @tbls);
                           -- SELECT @delStmt;
                           PREPARE stmt FROM @delStmt;
                           EXECUTE stmt;
                           DEALLOCATE PREPARE stmt;' \\
                %(db_name)s
            """) % context
        )
        if context['crontab']:
            context['crontab_regex'] = '\\|'.join(context['crontab'].splitlines())
            context['crontab_regex'] = context['crontab_regex'].replace('*', '\\*')
            self.append(textwrap.dedent("""\
                crontab -u %(user)s -l \\
                    | grep -v 'Moodle:"%(site_name)s"\\|%(crontab_regex)s' \\
                    | su - %(user)s --shell /bin/bash -c 'crontab'
                """) % context
            )
        self.delete_site_map(context)
    
    def get_context(self, saas):
        context = {
            'banner': self.get_banner(),
            'name': saas.name,
            'site_name': saas.name,
            'full_name': "%s course" % saas.name.capitalize(),
            'moodle_path': settings.SAAS_MOODLE_PATH,
            'user': settings.SAAS_MOODLE_SYSTEMUSER,
            'db_user': settings.SAAS_MOODLE_DB_USER,
            'db_pass': settings.SAAS_MOODLE_DB_PASS,
            'db_name': settings.SAAS_MOODLE_DB_NAME,
            'db_host': settings.SAAS_MOODLE_DB_HOST,
            'db_prefix': saas.name.replace('-', '_'),
            'email': saas.account.email,
            'password': getattr(saas, 'password', None),
            'custom_url': saas.custom_url.rstrip('/'),
            'custom_domain': urlparse(saas.custom_url).netloc if saas.custom_url else None,
        }
        context.update({
            'crontab': settings.SAAS_MOODLE_CRONTAB % context,
            'db_name': context['db_name'] % context,
            'moodledata_path': settings.SAAS_MOODLE_DATA_PATH % context,
        })
        return context

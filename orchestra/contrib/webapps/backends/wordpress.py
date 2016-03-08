import os
import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController, replace

from .. import settings

from . import WebAppServiceMixin


# Based on https://github.com/mtomic/wordpress-install/blob/master/wpinstall.php
class WordPressController(WebAppServiceMixin, ServiceController):
    """
    Installs the latest version of WordPress available on www.wordpress.org
    It fully configures the wp-config.php (keys included) and sets up the database with initial admin password.
    """
    verbose_name = _("Wordpress")
    model = 'webapps.WebApp'
    default_route_match = "webapp.type == 'wordpress-php'"
    script_executable = '/usr/bin/php'
    doc_settings = (settings,
        ('WEBAPPS_DEFAULT_MYSQL_DATABASE_HOST',)
    )
    
    def prepare(self):
        self.append(textwrap.dedent("""\
            <?php
            function exc($cmd) {
                passthru($cmd, $exit_code);
                if ($exit_code != 0) {
                    echo "ERROR: execution returned non-zero code: $exit_code. cmd was:\\n$cmd\\n";
                    exit($exit_code);
                }
            }
            function wp_new_blog_notification($blog_title, $blog_url, $user_id, $password){
                // do nothing
            }""")
        )
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.append(textwrap.dedent("""\
            if (count(glob("%(app_path)s/*")) > 1) {
                die("App directory not empty.");
            }
            // Download and untar wordpress (with caching system)
            shell_exec("mkdir -p %(app_path)s
                # Prevent other backends from writting here
                touch %(app_path)s/.lock
                filename=\\$(wget https://wordpress.org/latest.tar.gz --server-response --spider --no-check-certificate 2>&1 \\
                    | grep filename | cut -d'=' -f2)
                mkdir -p %(cms_cache_dir)s
                if [ ! -e %(cms_cache_dir)s/wordpress ] || [ \\$(basename \\$(readlink %(cms_cache_dir)s/wordpress) 2> /dev/null ) != \\$filename ]; then
                    wget https://wordpress.org/latest.tar.gz -O - --no-check-certificate \\
                        | tee %(cms_cache_dir)s/\\$filename \\
                        | tar -xzvf - -C %(app_path)s --strip-components=1
                    rm -f %(cms_cache_dir)s/wordpress
                    ln -s %(cms_cache_dir)s/\\$filename %(cms_cache_dir)s/wordpress
                else
                    tar -xzvf %(cms_cache_dir)s/wordpress -C %(app_path)s --strip-components=1
                fi
                mkdir %(app_path)s/wp-content/uploads
                chmod 750 %(app_path)s/wp-content/uploads
                rm %(app_path)s/.lock
                ");
            
            $config_file = file('%(app_path)s/' . 'wp-config-sample.php');
            $secret_keys = file_get_contents('https://api.wordpress.org/secret-key/1.1/salt/');
            $secret_keys = explode( "\\n", $secret_keys );
            foreach ( $secret_keys as $k => $v ) {
                $secret_keys[$k] = substr( $v, 28, 64 );
            }
            array_pop($secret_keys);
            
            // setup wordpress database and keys config
            $config_file = str_replace('database_name_here', "%(db_name)s", $config_file);
            $config_file = str_replace('username_here', "%(db_user)s", $config_file);
            $config_file = str_replace('password_here', "%(password)s", $config_file);
            $config_file = str_replace('localhost', "%(db_host)s", $config_file);
            $config_file = str_replace("'AUTH_KEY',         'put your unique phrase here'", "'AUTH_KEY',         '{$secret_keys[0]}'", $config_file);
            $config_file = str_replace("'SECURE_AUTH_KEY',  'put your unique phrase here'", "'SECURE_AUTH_KEY',  '{$secret_keys[1]}'", $config_file);
            $config_file = str_replace("'LOGGED_IN_KEY',    'put your unique phrase here'", "'LOGGED_IN_KEY',    '{$secret_keys[2]}'", $config_file);
            $config_file = str_replace("'NONCE_KEY',        'put your unique phrase here'", "'NONCE_KEY',        '{$secret_keys[3]}'", $config_file);
            $config_file = str_replace("'AUTH_SALT',        'put your unique phrase here'", "'AUTH_SALT',        '{$secret_keys[4]}'", $config_file);
            $config_file = str_replace("'SECURE_AUTH_SALT', 'put your unique phrase here'", "'SECURE_AUTH_SALT', '{$secret_keys[5]}'", $config_file);
            $config_file = str_replace("'LOGGED_IN_SALT',   'put your unique phrase here'", "'LOGGED_IN_SALT',   '{$secret_keys[6]}'", $config_file);
            $config_file = str_replace("'NONCE_SALT',       'put your unique phrase here'", "'NONCE_SALT',       '{$secret_keys[7]}'", $config_file);
            
            if(file_exists('%(app_path)s/' .'wp-config.php')) {
                unlink('%(app_path)s/' .'wp-config.php');
            }
            
            $fw = fopen('%(app_path)s/' . 'wp-config.php', 'a');
            foreach ( $config_file as $line_num => $line ) {
                fwrite($fw, $line);
            }
            exc('chown -R %(user)s:%(group)s %(app_path)s');
            
            // Run wordpress installation process
            
            define('WP_CONTENT_DIR', 'wp-content/');
            define('WP_LANG_DIR', WP_CONTENT_DIR . '/languages' );
            define('WP_USE_THEMES', true);
            define('DB_NAME', "%(db_name)s");
            define('DB_USER', "%(db_user)s");
            define('DB_PASSWORD', "%(password)s");
            define('DB_HOST', "%(db_host)s");
            
            $_GET['step'] = 2;
            $_POST['weblog_title'] = "%(title)s";
            $_POST['user_name'] = "admin";
            $_POST['admin_email'] = "%(email)s";
            $_POST['blog_public'] = true;
            $_POST['admin_password'] = "%(password)s";
            $_POST['admin_password2'] = "%(password)s";
            
            ob_start();
            require_once('%(app_path)s/wp-admin/install.php');
            $response = ob_get_contents();
            ob_end_clean();
            if (strpos($response, '<h1>Success!</h1>') === false) {
                echo "Error has occured during installation\\n";
                echo $msg;
                exit(1);
            }""") % context
        )
    
    def commit(self):
        self.append('?>')
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.append("exc('rm -rf %(app_path)s');" % context)
    
    def get_context(self, webapp):
        context = super(WordPressController, self).get_context(webapp)
        context.update({
            'db_name': webapp.data['db_name'],
            'db_user': webapp.data['db_user'],
            'password': webapp.data['password'],
            'db_host': settings.WEBAPPS_DEFAULT_MYSQL_DATABASE_HOST,
            'email': webapp.account.email,
            'title': "%s blog's" % webapp.account.get_full_name(),
            'cms_cache_dir': os.path.normpath(settings.WEBAPPS_CMS_CACHE_DIR)
        })
        return replace(context, '"', "'")

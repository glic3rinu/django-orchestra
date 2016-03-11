import os
import textwrap

from orchestra.contrib.orchestration import ServiceController


class WordPressURLController(ServiceController):
    """
    Configures WordPress site URL with associated website domain.
    """
    verbose_name = "WordPress URL"
    model = 'websites.Content'
    default_route_match = "content.webapp.type == 'wordpress-php'"
    
    def save(self, content):
        context = self.get_context(content)
        if context['url']:
            self.append(textwrap.dedent("""\
                mysql %(db_name)s -e 'UPDATE wp_options
                                      SET option_value="%(url)s"
                                      WHERE option_id IN (1, 2) AND option_value="http:";'
                """) % context
            )
    
    def delete(self, content):
        context = self.get_context(content)
        self.append(textwrap.dedent("""\
            mysql %(db_name)s -e 'UPDATE wp_options
                                  SET option_value="http:"
                                  WHERE option_id IN (1, 2);'
            """) % context
        )
    
    def get_context(self, content):
        return {
            'url': content.get_absolute_url(),
            'db_name': content.webapp.data.get('db_name'),
        }


class WordPressForceSSLController(ServiceController):
    """ sets FORCE_SSL_ADMIN to true when website supports HTTPS """
    verbose_name = "WordPress Force SSL"
    model = 'websites.Content'
    related_models = (
        ('websites.Website', 'content_set'),
    )
    default_route_match = "content.webapp.type == 'wordpress-php'"
    
    def save(self, content):
        context = self.get_context(content)
        site = content.website
        if site.protocol in (site.HTTP_AND_HTTPS, site.HTTPS_ONLY, site.HTTPS):
            self.append(textwrap.dedent("""
                if [[ ! $(grep FORCE_SSL_ADMIN %(wp_conf_path)s) ]]; then
                    echo "Enabling FORCE_SSL_ADMIN for %(webapp_name)s webapp"
                    sed -i -E "s#^(define\('NONCE_SALT.*)#\\1\\n\\ndefine\('FORCE_SSL_ADMIN', true\);#" \\
                        %(wp_conf_path)s
                fi""") % context
            )
    
    def get_context(self, content):
        return {
            'webapp_name': content.webapp.name,
            'wp_conf_path': os.path.join(content.webapp.get_path(), 'wp-config.php'),
        }

from django.utils.translation import ugettext_lazy as _

from .cms import CMSApp


class WordPressApp(CMSApp):
    name = 'wordpress-php'
    verbose_name = "WordPress"
    help_text = _(
        "This installs the latest version of WordPress into the webapp directory.<br>"
        "A database and database user will automatically be created for this webapp.<br>"
        "This installer creates a user 'admin' with a randomly generated password.<br>"
        "The password will be visible in the 'password' field after the installer has finished."
    )
    icon = 'orchestra/icons/apps/WordPress.png'
    db_prefix = 'wp_'
    
    def get_detail(self):
        return self.instance.data.get('php_version', '')
